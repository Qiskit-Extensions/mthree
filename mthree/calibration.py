# This code is part of Mthree.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=no-name-in-module
"""mthree calibration"""

import threading
import datetime
import numpy as np
from qiskit import QuantumCircuit, transpile, execute
from qiskit.providers import BaseBackend

def _tensor_meas_states(qubit, num_qubits, initial_reset=False):
    """Construct |0> and |1> states
    for independent 1Q cals.
    """
    qc0 = QuantumCircuit(num_qubits, 1)
    if initial_reset:
        qc0.reset(qubit)
    qc0.measure(qubit, 0)
    qc1 = QuantumCircuit(num_qubits, 1)
    if initial_reset:
        qc1.reset(qubit)
    qc1.x(qubit)
    qc1.measure(qubit, 0)
    return [qc0, qc1]


def _marg_meas_states(num_qubits, initial_reset=False):
    """Construct all zeros and all ones states
    for marginal 1Q cals.
    """
    qc0 = QuantumCircuit(num_qubits)
    if initial_reset:
        qc0.reset(range(num_qubits))
    qc0.measure_all()
    qc1 = QuantumCircuit(num_qubits)
    if initial_reset:
        qc1.reset(range(num_qubits))
    qc1.x(range(num_qubits))
    qc1.measure_all()
    return [qc0, qc1]


def _balanced_cal_strings(num_qubits):
    """Compute the 2*num_qubits strings for balanced calibration.

    Parameters:
        num_qubits (int): Number of qubits to be measured.

    Returns:
        list: List of strings for balanced calibration circuits.
    """
    strings = []
    for rep in range(1, num_qubits+1):
        str1 = ''
        str2 = ''
        for jj in range(int(np.ceil(num_qubits / rep))):
            str1 += str(jj % 2) * rep
            str2 += str((jj+1) % 2) * rep

        strings.append(str1[:num_qubits])
        strings.append(str2[:num_qubits])
    return strings


def _balanced_cal_circuits(cal_strings, initial_reset=False):
    """Build balanced calibration circuits.

    Parameters:
        cal_strings (list): List of strings for balanced cal circuits.

    Returns:
        list: List of balanced cal circuits.
    """
    num_qubits = len(cal_strings[0])
    circs = []
    for string in cal_strings:
        qc = QuantumCircuit(num_qubits)
        if initial_reset:
            qc.reset(range(num_qubits))
        for idx, bit in enumerate(string[::-1]):
            if bit == '1':
                qc.x(idx)
        qc.measure_all()
        circs.append(qc)
    return circs


def grab_additional_cals(mitigator, qubits, shots=None, method='balanced', rep_delay=None,
                          initial_reset=False):
    """Grab missing calibration data from backend.

    Parameters:
        qubits (array_like): List of measured qubits.
        shots (int): Number of shots to take, min(1e4, max_shots).
        method (str): Type of calibration, 'balanced' (default), 'independent', or 'marginal'.
        rep_delay (float): Delay between circuits on IBM Quantum backends.
        initial_reset (bool): Use resets at beginning of calibration circuits, default=False.

    Raises:
        M3Error: Backend not set.
        M3Error: Faulty qubits found.
    """
    if mitigator.system is None:
        raise M3Error("System is not set.  Use 'cals_from_file'.")
    if mitigator.single_qubit_cals is None:
        mitigator.single_qubit_cals = [None] * mitigator.num_qubits
    if mitigator.cal_shots is None:
        if shots is None:
            shots = min(mitigator.system.configuration().max_shots, 10000)
        mitigator.cal_shots = shots
    if mitigator.rep_delay is None:
        mitigator.rep_delay = rep_delay

    if method not in ['independent', 'balanced', 'marginal']:
        raise M3Error('Invalid calibration method.')

    if isinstance(qubits, dict):
        # Assuming passed a mapping
        qubits = list(qubits)
    elif isinstance(qubits, list):
        # Check if passed a list of mappings
        if isinstance(qubits[0], dict):
            # Assuming list of mappings, need to get unique elements
            _qubits = []
            for item in qubits:
                _qubits.extend(list(item))
            qubits = list(set(_qubits))

    num_cal_qubits = len(qubits)
    cal_strings = []
    if method == 'marginal':
        circs = _marg_meas_states(num_cal_qubits, initial_reset=initial_reset)
        trans_qcs = transpile(circs, mitigator.system,
                              initial_layout=qubits, optimization_level=0)
    elif method == 'balanced':
        cal_strings = _balanced_cal_strings(num_cal_qubits)
        circs = _balanced_cal_circuits(cal_strings, initial_reset=initial_reset)
        trans_qcs = transpile(circs, mitigator.system,
                              initial_layout=qubits, optimization_level=0)
    # Indeopendent
    else:
        circs = []
        for kk in qubits:
            circs.extend(_tensor_meas_states(kk, mitigator.num_qubits,
                                             initial_reset=initial_reset))
        trans_qcs = transpile(circs, mitigator.system, optimization_level=0)

    # This BaseBackend check is here for Qiskit direct access.  Should be removed later.
    if isinstance(mitigator.system, BaseBackend):
        job = execute(trans_qcs, mitigator.system, optimization_level=0,
                      shots=mitigator.cal_shots, rep_delay=mitigator.rep_delay)
    else:
        job = mitigator.system.run(trans_qcs, shots=mitigator.cal_shots, rep_delay=mitigator.rep_delay)

    # Execute job and cal building in new theread.
    mitigator._job_error = None
    thread = threading.Thread(target=_job_thread, args=(job, mitigator, method, qubits,
                                                        num_cal_qubits, cal_strings))
    mitigator._thread = thread
    mitigator._thread.start()

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
    timestamp = ""
    if hasattr(res, "date"):
        timestamp = res.date
    # Needed since Aer result date is str but IBMQ job is datetime
    if isinstance(timestamp, datetime.datetime):
        timestamp = timestamp.isoformat()
    mit.cal_timestamp = timestamp
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
            denom = mit.cal_shots * num_cal_qubits

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

        for jj, cal in enumerate(cals):
            cal[1, 0] = 1.0 - cal[0, 0]
            cal[0, 1] = 1.0 - cal[1, 1]

            if cal[0, 1] >= cal[0, 0]:
                bad_list.append(qubits[jj])

        for idx, cal in enumerate(cals):
            mit.single_qubit_cals[qubits[idx]] = cal

    if any(bad_list):
        mit._job_error = M3Error('Faulty qubits detected: {}'.format(bad_list))
