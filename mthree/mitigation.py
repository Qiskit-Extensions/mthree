# This code is part of Mthree.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=no-name-in-module, invalid-name
"""Calibration data"""

import warnings
import threading
import datetime
from time import perf_counter

import psutil
import numpy as np
import scipy.linalg as la
import scipy.sparse.linalg as spla
import orjson
from qiskit import execute
from qiskit.providers import Backend

from mthree.circuits import (_tensor_meas_states, _marg_meas_states,
                             balanced_cal_strings, balanced_cal_circuits)
from mthree.matrix import _reduced_cal_matrix, sdd_check
from mthree.utils import counts_to_vector, vector_to_quasiprobs
from mthree.norms import ainv_onenorm_est_lu, ainv_onenorm_est_iter
from mthree.matvec import M3MatVec
from mthree.exceptions import M3Error
from mthree.classes import QuasiCollection
from ._helpers import system_info


class M3Mitigation():
    """Main M3 calibration class."""
    def __init__(self, system=None, iter_threshold=4096):
        """Main M3 calibration class.

        Parameters:
            system (Backend): Target backend.
            iter_threshold (int): Sets the bitstring count at which iterative mode
                                  is turned on (assuming reasonable error rates).

        Attributes:
            system (Backend): The target system.
            system_info (dict): Information needed about the system
            cal_method (str): Calibration method used
            cal_timestamp (str): Time at which cals were taken
            single_qubit_cals (list): 1Q calibration matrices
        """
        self.system = system
        self.system_info = system_info(system) if system else {}
        self.single_qubit_cals = None
        self.num_qubits = self.system_info["num_qubits"] if system else None
        self.iter_threshold = iter_threshold
        self.cal_shots = None
        self.cal_method = 'balanced'
        self.cal_timestamp = None  # The time at which the cals result was generated
        self.rep_delay = None
        # attributes for handling threaded job
        self._thread = None
        self._job_error = None
        # Holds the cals file
        self.cals_file = None
        # faulty qubits
        self.faulty_qubits = []

    def __getattribute__(self, attr):
        """This allows for checking the status of the threaded cals call

        For certain attr this will join the thread and/or raise an error.
        """
        __dict__ = super().__getattribute__('__dict__')
        if attr in __dict__:
            if attr in ['single_qubit_cals']:
                self._thread_check()
        return super().__getattribute__(attr)

    def _form_cals(self, qubits):
        """Form the 1D cals array from tensored cals data

        Parameters:
            qubits (array_like): The qubits to calibrate over.

        Returns:
            ndarray: 1D Array of float cals data.
        """
        qubits = np.asarray(qubits, dtype=int)
        cals = np.zeros(4*qubits.shape[0], dtype=float)

        # Reverse index qubits for easier indexing later
        for kk, qubit in enumerate(qubits[::-1]):
            cals[4*kk:4*kk+4] = self.single_qubit_cals[qubit].ravel()
        return cals

    def _check_sdd(self, counts, qubits, distance=None):
        """Checks if reduced A-matrix is SDD or not

        Parameters:
            counts (dict): Dictionary of counts.
            qubits (array_like): List of qubits.
            distance (int): Distance to compute over.

        Returns:
            bool: True if A-matrix is SDD, else False

        Raises:
            M3Error: Number of qubits supplied does not match bit-string length.
        """
        # If distance is None, then assume max distance.
        num_bits = len(qubits)
        if distance is None:
            distance = num_bits

        # check if len of bitstrings does not equal number of qubits passed.
        bitstring_len = len(next(iter(counts)))
        if bitstring_len != num_bits:
            raise M3Error('Bitstring length ({}) does not match'.format(bitstring_len) +
                          ' number of qubits ({})'.format(num_bits))
        cals = self._form_cals(qubits)
        return sdd_check(counts, cals, num_bits, distance)

    def tensored_cals_from_system(self, qubits=None, shots=None,  method='balanced',
                                  rep_delay=None, cals_file=None):
        """Grab calibration data from system.

        Parameters:
            qubits (array_like): Qubits over which to correct calibration data. Default is all.
            shots (int): Number of shots per circuit. Default is min(1e4, max_shots).
            method (str): Type of calibration, 'balanced' (default), 'independent', or 'marginal'.
            rep_delay (float): Delay between circuits on IBM Quantum backends.
            cals_file (str): Output path to write JSON calibration data to.
        """
        warnings.warn("This method is deprecated, use 'cals_from_system' instead.")
        self.cals_from_system(qubits=qubits, shots=shots, method=method,
                              rep_delay=rep_delay,
                              cals_file=cals_file)

    def cals_from_system(self, qubits=None, shots=None, method=None,
                         initial_reset=False, rep_delay=None, cals_file=None,
                         async_cal=False):
        """Grab calibration data from system.

        Parameters:
            qubits (array_like): Qubits over which to correct calibration data. Default is all.
            shots (int): Number of shots per circuit. min(1e4, max_shots).
            method (str): Type of calibration, 'balanced' (default for hardware),
                         'independent' (default for simulators), or 'marginal'.
            initial_reset (bool): Use resets at beginning of calibration circuits, default=False.
            rep_delay (float): Delay between circuits on IBM Quantum backends.
            cals_file (str): Output path to write JSON calibration data to.
            async_cal (bool): Do calibration async in a separate thread, default is False.

        Raises:
            M3Error: Called while a calibration currently in progress.
        """
        if self._thread:
            raise M3Error('Calibration currently in progress.')
        if qubits is None:
            qubits = range(self.num_qubits)
        if method is None:
            method = 'balanced'
            if self.system_info["simulator"]:
                method = 'independent'
        self.cal_method = method
        self.rep_delay = rep_delay
        self.cals_file = cals_file
        self.cal_timestamp = None
        self._grab_additional_cals(qubits, shots=shots,  method=method,
                                   rep_delay=rep_delay, initial_reset=initial_reset,
                                   async_cal=async_cal)

    def cals_from_file(self, cals_file):
        """Generated the calibration data from a previous runs output

        Parameters:
            cals_file (str): A string path to the saved counts file from an
                             earlier run.
        Raises:
                M3Error: Calibration in progress.
        """
        if self._thread:
            raise M3Error('Calibration currently in progress.')
        with open(cals_file, 'r', encoding='utf-8') as fd:
            loaded_data = orjson.loads(fd.read())
            if isinstance(loaded_data, dict):
                self.single_qubit_cals = [np.asarray(cal) if cal else None
                                          for cal in loaded_data['cals']]
                self.cal_timestamp = loaded_data['timestamp']
                self.cal_shots = loaded_data.get('shots', None)
            else:
                warnings.warn('Loading from old M3 file format.  Save again to update.')
                self.cal_timestamp = None
                self.cal_shots = None
                self.single_qubit_cals = [np.asarray(cal) if cal else None
                                          for cal in loaded_data]
        self.faulty_qubits = _faulty_qubit_checker(self.single_qubit_cals)

    def cals_to_file(self, cals_file=None):
        """Save calibration data to JSON file.

        Parameters:
            cals_file (str): File in which to store calibrations.

        Raises:
            M3Error: Calibration filename missing.
            M3Error: Mitigator is not calibrated.
        """
        if not cals_file:
            raise M3Error('cals_file must be explicitly set.')
        if not self.single_qubit_cals:
            raise M3Error('Mitigator is not calibrated.')
        save_dict = {'timestamp': self.cal_timestamp,
                     'backend': self.system_info.get("name", None),
                     'shots': self.cal_shots,
                     'cals': self.single_qubit_cals}
        with open(cals_file, 'wb') as fd:
            fd.write(orjson.dumps(save_dict,
                                  option=orjson.OPT_SERIALIZE_NUMPY))

    def tensored_cals_from_file(self, cals_file):
        """Generated the tensored calibration data from a previous runs output

        Parameters:
            cals_file (str): A string path to the saved counts file from an
                             earlier run.
        """
        warnings.warn("This method is deprecated, use 'cals_from_file' instead.")
        self.cals_from_file(cals_file)

    def cals_from_matrices(self, matrices):
        """Init calibration data from list of NumPy arrays.

        Missing entires are set to None elements.

        Parameters:
            matrices (list_like): List of cals as NumPy arrays

        Raises:
            M3Error: If system set error if list length != num_qubits on system
        """
        matrices = list(matrices)
        if self.num_qubits:
            if len(matrices) != self.num_qubits:
                raise M3Error('Input list length not equal to'
                              ' number of qubits {} != {}'.format(len(matrices), self.num_qubits))
        self.single_qubit_cals = matrices
        self.faulty_qubits = _faulty_qubit_checker(self.single_qubit_cals)

    def cals_to_matrices(self):
        """Return single qubit cals as list of NumPy arrays

        Returns:
            list: List of cals as NumPy arrays
        """
        return self.single_qubit_cals.copy()

    def _grab_additional_cals(self, qubits, shots=None, method='balanced', rep_delay=None,
                              initial_reset=False, async_cal=False):
        """Grab missing calibration data from backend.

        Parameters:
            qubits (array_like): List of measured qubits.
            shots (int): Number of shots to take, min(1e4, max_shots).
            method (str): Type of calibration, 'balanced' (default), 'independent', or 'marginal'.
            rep_delay (float): Delay between circuits on IBM Quantum backends.
            initial_reset (bool): Use resets at beginning of calibration circuits, default=False.
            async_cal (bool): Do calibration async in a separate thread, default is False.

        Raises:
            M3Error: Backend not set.
            M3Error: Faulty qubits found.
        """
        if self.system is None:
            raise M3Error("System is not set.  Use 'cals_from_file'.")
        if self.single_qubit_cals is None:
            self.single_qubit_cals = [None]*self.num_qubits
        if self.cal_shots is None:
            if shots is None:
                shots = min(self.system_info["max_shots"], 10000)
            self.cal_shots = shots
        if self.rep_delay is None:
            self.rep_delay = rep_delay

        if method not in ['independent', 'balanced', 'marginal']:
            raise M3Error('Invalid calibration method.')

        if isinstance(qubits, dict):
            # Assuming passed a mapping
            qubits = list(set(qubits.values()))
        elif isinstance(qubits, list):
            # Check if passed a list of mappings
            if isinstance(qubits[0], dict):
                # Assuming list of mappings, need to get unique elements
                _qubits = []
                for item in qubits:
                    _qubits.extend(list(set(item.values())))
                qubits = list(set(_qubits))

        num_cal_qubits = len(qubits)
        cal_strings = []
        # shots is needed here because balanced cals will use a value
        # different from cal_shots
        shots = self.cal_shots
        if method == 'marginal':
            trans_qcs = _marg_meas_states(qubits, self.num_qubits,
                                          initial_reset=initial_reset)

        elif method == 'balanced':
            cal_strings = balanced_cal_strings(num_cal_qubits)
            trans_qcs = balanced_cal_circuits(cal_strings, qubits,
                                              self.num_qubits,
                                              initial_reset=initial_reset)
            shots = (self.cal_shots + 1) // num_cal_qubits
        # Independent
        else:
            trans_qcs = []
            for kk in qubits:
                trans_qcs.extend(_tensor_meas_states(kk, self.num_qubits,
                                                     initial_reset=initial_reset))

        # This Backend check is here for Qiskit direct access.  Should be removed later.
        if not isinstance(self.system, Backend):
            job = execute(trans_qcs, self.system, optimization_level=0,
                          shots=shots, rep_delay=self.rep_delay)
        else:
            job = self.system.run(trans_qcs, shots=shots, rep_delay=self.rep_delay)

        # Execute job and cal building in new theread.
        self._job_error = None
        if async_cal:
            thread = threading.Thread(target=_job_thread, args=(job, self, method, qubits,
                                                                num_cal_qubits, cal_strings))
            self._thread = thread
            self._thread.start()
        else:
            _job_thread(job, self, method, qubits, num_cal_qubits, cal_strings)

    def apply_correction(self, counts, qubits, distance=None,
                         method='auto',
                         max_iter=25, tol=1e-5,
                         return_mitigation_overhead=False,
                         details=False):
        """Applies correction to given counts.

        Parameters:
            counts (dict, list): Input counts dict or list of dicts.
            qubits (dict, array_like): Qubits on which measurements applied.
            distance (int): Distance to correct for. Default=num_bits
            method (str): Solution method: 'auto', 'direct' or 'iterative'.
            max_iter (int): Max. number of iterations, Default=25.
            tol (float): Convergence tolerance of iterative method, Default=1e-5.
            return_mitigation_overhead (bool): Returns the mitigation overhead, default=False.
            details (bool): Return extra info, default=False.

        Returns:
            QuasiDistribution or QuasiCollection: Dictionary of quasiprobabilities if
                                                  input is a single dict, else a collection
                                                  of quasiprobabilities.

        Raises:
            M3Error: Bitstring length does not match number of qubits given.
        """
        if len(counts) == 0:
            raise M3Error('Input counts is any empty dict.')
        given_list = False
        if isinstance(counts, (list, np.ndarray)):
            given_list = True
        if not given_list:
            counts = [counts]

        if isinstance(qubits, dict):
            # If a mapping was given for qubits
            qubits = [list(qubits.values())]
        elif not any(isinstance(qq, (list, tuple, np.ndarray, dict)) for qq in qubits):
            qubits = [qubits]*len(counts)
        else:
            if isinstance(qubits[0], dict):
                # assuming passed a list of mappings
                qubits = [list(qu.values()) for qu in qubits]

        if len(qubits) != len(counts):
            raise M3Error('Length of counts does not match length of qubits.')

        # Check if using faulty qubits
        bad_qubits = set()
        for item in qubits:
            for qu in item:
                if qu in self.faulty_qubits:
                    bad_qubits.add(qu)
        if any(bad_qubits):
            raise M3Error('Using faulty qubits: {}'.format(bad_qubits))

        quasi_out = []
        for idx, cnts in enumerate(counts):

            quasi_out.append(
                self._apply_correction(cnts, qubits=qubits[idx],
                                       distance=distance,
                                       method=method,
                                       max_iter=max_iter, tol=tol,
                                       return_mitigation_overhead=return_mitigation_overhead,
                                       details=details)
                            )

        if not given_list:
            return quasi_out[0]
        return QuasiCollection(quasi_out)

    def _apply_correction(self, counts, qubits, distance=None,
                          method='auto',
                          max_iter=25, tol=1e-5,
                          return_mitigation_overhead=False,
                          details=False):
        """Applies correction to given counts.

        Parameters:
            counts (dict): Input counts dict.
            qubits (array_like): Qubits on which measurements applied.
            distance (int): Distance to correct for. Default=num_bits
            method (str): Solution method: 'auto', 'direct' or 'iterative'.
            max_iter (int): Max. number of iterations, Default=25.
            tol (float): Convergence tolerance of iterative method, Default=1e-5.
            return_mitigation_overhead (bool): Returns the mitigation overhead, default=False.
            details (bool): Return extra info, default=False.

        Returns:
            QuasiDistribution: Dictionary of quasiprobabilities.

        Raises:
            M3Error: Bitstring length does not match number of qubits given.
        """
        # This is needed because counts is a Counts object in Qiskit not a dict.
        counts = dict(counts)
        shots = sum(counts.values())

        # If distance is None, then assume max distance.
        num_bits = len(qubits)
        num_elems = len(counts)
        if distance is None:
            distance = num_bits

        # check if len of bitstrings does not equal number of qubits passed.
        bitstring_len = len(next(iter(counts)))
        if bitstring_len != num_bits:
            raise M3Error('Bitstring length ({}) does not match'.format(bitstring_len) +
                          ' number of qubits ({})'.format(num_bits))

        # Check if no cals done yet
        if self.single_qubit_cals is None:
            warnings.warn('No calibration data. Calibrating: {}'.format(qubits))
            self._grab_additional_cals(qubits, method=self.cal_method)

        # Check if one or more new qubits need to be calibrated.
        missing_qubits = [qq for qq in qubits if self.single_qubit_cals[qq] is None]
        if any(missing_qubits):
            warnings.warn('Computing missing calibrations for qubits: {}'.format(missing_qubits))
            self._grab_additional_cals(missing_qubits, method=self.cal_method)

        if method == 'auto':
            current_free_mem = psutil.virtual_memory().available / 1024**3
            # First check if direct method can be run
            if num_elems <= self.iter_threshold \
                    and ((num_elems**2+num_elems)*8/1024**3 < current_free_mem/2):
                method = 'direct'
            else:
                method = 'iterative'

        if method == 'direct':
            st = perf_counter()
            mit_counts, col_norms, gamma = self._direct_solver(counts, qubits, distance,
                                                               return_mitigation_overhead)
            dur = perf_counter()-st
            mit_counts.shots = shots
            if gamma is not None:
                mit_counts.mitigation_overhead = gamma * gamma
            if details:
                info = {'method': 'direct', 'time': dur, 'dimension': num_elems}
                info['col_norms'] = col_norms
                return mit_counts, info
            return mit_counts

        elif method == 'iterative':
            iter_count = np.zeros(1, dtype=int)

            def callback(_):
                iter_count[0] += 1

            if details:
                st = perf_counter()
                mit_counts, col_norms, gamma = self._matvec_solver(counts,
                                                                   qubits,
                                                                   distance,
                                                                   tol,
                                                                   max_iter,
                                                                   1,
                                                                   callback,
                                                                   return_mitigation_overhead)
                dur = perf_counter()-st
                mit_counts.shots = shots
                if gamma is not None:
                    mit_counts.mitigation_overhead = gamma * gamma
                info = {'method': 'iterative', 'time': dur, 'dimension': num_elems}
                info['iterations'] = iter_count[0]
                info['col_norms'] = col_norms
                return mit_counts, info
            # pylint: disable=unbalanced-tuple-unpacking
            mit_counts, gamma = self._matvec_solver(counts, qubits, distance, tol,
                                                    max_iter, 0, None,
                                                    return_mitigation_overhead)
            mit_counts.shots = shots
            if gamma is not None:
                mit_counts.mitigation_overhead = gamma * gamma
            return mit_counts

        else:
            raise M3Error('Invalid method: {}'.format(method))

    def reduced_cal_matrix(self, counts, qubits, distance=None):
        """Return the reduced calibration matrix used in the solution.

        Parameters:
            counts (dict): Input counts dict.
            qubits (array_like): Qubits on which measurements applied.
            distance (int): Distance to correct for. Default=num_bits

        Returns:
            ndarray: 2D array of reduced calibrations.
            dict: Counts in order they are displayed in matrix.

        Raises:
            M3Error: If bit-string length does not match passed number
                     of qubits.
        """
        counts = dict(counts)
        # If distance is None, then assume max distance.
        num_bits = len(qubits)
        if distance is None:
            distance = num_bits

        # check if len of bitstrings does not equal number of qubits passed.
        bitstring_len = len(next(iter(counts)))
        if bitstring_len != num_bits:
            raise M3Error('Bitstring length ({}) does not match'.format(bitstring_len) +
                          ' number of qubits ({})'.format(num_bits))

        cals = self._form_cals(qubits)
        A, counts, _ = _reduced_cal_matrix(counts, cals, num_bits, distance)
        return A, counts

    def _direct_solver(self, counts, qubits, distance=None,
                       return_mitigation_overhead=False):
        """Apply the mitigation using direct LU factorization.

        Parameters:
            counts (dict): Input counts dict.
            qubits (int): Qubits over which to calibrate.
            distance (int): Distance to correct for. Default=num_bits
            return_mitigation_overhead (bool): Returns the mitigation overhead, default=False.

        Returns:
            QuasiDistribution: dict of Quasiprobabilites
        """
        cals = self._form_cals(qubits)
        num_bits = len(qubits)
        A, sorted_counts, col_norms = _reduced_cal_matrix(counts, cals, num_bits, distance)
        vec = counts_to_vector(sorted_counts)
        LU = la.lu_factor(A, check_finite=False)
        x = la.lu_solve(LU, vec, check_finite=False)
        gamma = None
        if return_mitigation_overhead:
            gamma = ainv_onenorm_est_lu(A, LU)
        out = vector_to_quasiprobs(x, sorted_counts)
        return out, col_norms, gamma

    def _matvec_solver(self, counts, qubits, distance, tol=1e-5, max_iter=25,
                       details=0, callback=None,
                       return_mitigation_overhead=False):
        """Compute solution using GMRES and Jacobi preconditioning.

        Parameters:
            counts (dict): Input counts dict.
            qubits (int): Qubits over which to calibrate.
            tol (float): Tolerance to use.
            max_iter (int): Maximum number of iterations to perform.
            distance (int): Distance to correct for. Default=num_bits
            details (bool): Return col norms.
            callback (callable): Callback function to record iteration count.
            return_mitigation_overhead (bool): Returns the mitigation overhead, default=False.

        Returns:
            QuasiDistribution: dict of Quasiprobabilites

        Raises:
            M3Error: Solver did not converge.
        """
        cals = self._form_cals(qubits)
        M = M3MatVec(dict(counts), cals, distance)
        L = spla.LinearOperator((M.num_elems, M.num_elems),
                                matvec=M.matvec, rmatvec=M.rmatvec)
        diags = M.get_diagonal()

        def precond_matvec(x):
            out = x / diags
            return out

        P = spla.LinearOperator((M.num_elems, M.num_elems), precond_matvec)
        vec = counts_to_vector(M.sorted_counts)
        out, error = spla.gmres(L, vec, tol=tol, atol=tol, maxiter=max_iter,
                                M=P, callback=callback)
        if error:
            raise M3Error('GMRES did not converge: {}'.format(error))

        gamma = None
        if return_mitigation_overhead:
            gamma = ainv_onenorm_est_iter(M, tol=tol, max_iter=max_iter)

        quasi = vector_to_quasiprobs(out, M.sorted_counts)
        if details:
            return quasi, M.get_col_norms(), gamma
        return quasi, gamma

    def readout_fidelity(self, qubits=None):
        """Compute readout fidelity for calibrated qubits.

        Parameters:
            qubits (array_like): Qubits to compute over, default is all.

        Returns:
            list: List of qubit fidelities.

        Raises:
            M3Error: Mitigator is not calibrated.
            M3Error: Qubit indices out of range.
        """
        if self.single_qubit_cals is None:
            raise M3Error('Mitigator is not calibrated')

        if qubits is None:
            qubits = range(self.num_qubits)
        else:
            outliers = [kk for kk in qubits if kk >= self.num_qubits]
            if any(outliers):
                raise M3Error('One or more qubit indices out of range: {}'.format(outliers))
        fids = []
        for kk in qubits:
            qubit = self.single_qubit_cals[kk]
            if qubit is not None:
                fids.append(np.mean(qubit.diagonal()))
            else:
                fids.append(None)
        return fids

    def _thread_check(self):
        """Check if a thread is running and join it.

        Raise an error if one is given.
        """
        if self._thread and self._thread != threading.current_thread():
            self._thread.join()
            self._thread = None
        if self._job_error:
            raise self._job_error  # pylint: disable=raising-bad-type


def _job_thread(job, mit, method, qubits, num_cal_qubits, cal_strings):
    """Run the calibration job in a different thread and post-process

    Parameters:
        mit (M3Mitigator): The mitigator instance
        method (str): The type of calibration
        qubits (list): List of qubits used
        num_cal_qubits (int): Number of calibration qubits
        cal_strings (list): List of cal strings for balanced cals
    """
    try:
        res = job.result()
    # pylint: disable=broad-except
    except Exception as error:
        mit._job_error = error
        return
    counts = res.get_counts()
    # attach timestamp
    timestamp = res.date
    # Needed since Aer result date is str but IBMQ job is datetime
    if isinstance(timestamp, datetime.datetime):
        timestamp = timestamp.isoformat()
    # Go to UTC times because we are going to use this for
    # resultsDB storage as well
    dt = datetime.datetime.fromisoformat(timestamp)
    dt_utc = dt.astimezone(datetime.timezone.utc)
    mit.cal_timestamp = dt_utc.isoformat()
    # A list of qubits with bad meas cals
    bad_list = []
    if method == 'independent':
        for idx, qubit in enumerate(qubits):
            mit.single_qubit_cals[qubit] = np.zeros((2, 2), dtype=float)
            # Counts 0 has all P00, P10 data, so do that here
            prep0_counts = counts[2*idx]
            P10 = prep0_counts.get('1', 0) / mit.cal_shots
            P00 = 1-P10
            mit.single_qubit_cals[qubit][:, 0] = [P00, P10]
            # plus 1 here since zeros data at pos=0
            prep1_counts = counts[2*idx+1]
            P01 = prep1_counts.get('0', 0) / mit.cal_shots
            P11 = 1-P01
            mit.single_qubit_cals[qubit][:, 1] = [P01, P11]
            if P01 >= P00:
                bad_list.append(qubit)
    elif method == 'marginal':
        prep0_counts = counts[0]
        prep1_counts = counts[1]
        for idx, qubit in enumerate(qubits):
            mit.single_qubit_cals[qubit] = np.zeros((2, 2), dtype=float)
            count_vals = 0
            index = num_cal_qubits-idx-1
            for key, val in prep0_counts.items():
                if key[index] == '0':
                    count_vals += val
            P00 = count_vals / mit.cal_shots
            P10 = 1-P00
            mit.single_qubit_cals[qubit][:, 0] = [P00, P10]
            count_vals = 0
            for key, val in prep1_counts.items():
                if key[index] == '1':
                    count_vals += val
            P11 = count_vals / mit.cal_shots
            P01 = 1-P11
            mit.single_qubit_cals[qubit][:, 1] = [P01, P11]
            if P01 >= P00:
                bad_list.append(qubit)
    # balanced calibration
    else:
        cals = [np.zeros((2, 2), dtype=float) for kk in range(num_cal_qubits)]

        for idx, count in enumerate(counts):

            target = cal_strings[idx][::-1]
            good_prep = np.zeros(num_cal_qubits, dtype=float)
            denom = mit.cal_shots

            for key, val in count.items():
                key = key[::-1]
                for kk in range(num_cal_qubits):
                    if key[kk] == target[kk]:
                        good_prep[kk] += val

            for kk, cal in enumerate(cals):
                if target[kk] == '0':
                    cal[0, 0] += good_prep[kk] / denom
                else:
                    cal[1, 1] += good_prep[kk] / denom

        for cal in cals:
            cal[1, 0] = 1.0 - cal[0, 0]
            cal[0, 1] = 1.0 - cal[1, 1]

        for idx, cal in enumerate(cals):
            mit.single_qubit_cals[qubits[idx]] = cal

    # save cals to file, if requested
    if mit.cals_file:
        mit.cals_to_file(mit.cals_file)
    # faulty qubits, if any
    mit.faulty_qubits = _faulty_qubit_checker(mit.single_qubit_cals)


def _faulty_qubit_checker(cals):
    """Find faulty qubits in cals

    Parameters:
        cals (list): Input list of calibrations

    Returns:
        list: Faulty qubits
    """
    faulty_qubits = []
    for idx, cal in enumerate(cals):
        if cal is not None:
            if cal[0, 1] >= cal[0, 0]:
                faulty_qubits.append(idx)
    return faulty_qubits
