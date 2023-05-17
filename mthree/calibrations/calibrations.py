# This code is part of Mthree.
#
# (C) Copyright IBM 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=pointless-exception-statement
"""Calibration object"""
import threading
import warnings
import datetime
from dateutil import tz

from qiskit import QuantumCircuit

from mthree.exceptions import M3Error
from mthree._helpers import system_info
from mthree.generators import HadamardGenerator
from .mapping import calibration_mapping


class Calibration:
    """Calibration object"""

    def __init__(self, backend, qubits=None, generator=None):
        """Calibration object

        Parameters:
            backend (Backend): Target backend
            qubits (array_like): Physical qubits to calibrate over
            generator (Generator): Generator of calibration circuits
        """
        self.backend = backend
        self.backend_info = system_info(backend)
        # Auto populate qubits if None is given
        if qubits is None:
            qubits = range(self.backend_info["num_qubits"])
            # Remove faulty qubits if any
            if any(self.backend_info["inoperable_qubits"]):
                qubits = list(
                    filter(
                        lambda item: item not in self.backend_info["inoperable_qubits"],
                        list(range(self.backend_info["num_qubits"])),
                    )
                )
                warnings.warn(
                    "Backend reporting inoperable qubits. Skipping calibrations for: {}".format(
                        self.backend_info["inoperable_qubits"]
                    )
                )
        self.qubits = qubits
        if generator is None:
            gen = HadamardGenerator(len(self.qubits))
        else:
            gen = generator(len(self.qubits))
        self.generator = gen

        self.bit_to_physical_mapping = calibration_mapping(
            self.backend, qubits=self.qubits
        )
        self.physical_to_bit_mapping = {
            val: key for key, val in self.bit_to_physical_mapping.items()
        }
        self._calibration_data = None
        self.shots_per_circuit = None
        self.num_circuits = self.generator.length
        self.job_id = None
        self._timestamp = None
        self._thread = None
        self._job_error = None

    def __getattribute__(self, attr):
        """This allows for checking the status of the threaded cals call

        For certain attr this will join the thread and/or raise an error.
        """
        __dict__ = super().__getattribute__("__dict__")
        if attr in __dict__:
            if attr in ["_calibration_data", "timestamp"]:
                self._thread_check()
        return super().__getattribute__(attr)

    def _thread_check(self):
        """Check if a thread is running and join it.

        Raise an error if one is given.
        """
        if self._thread and self._thread != threading.current_thread():
            self._thread.join()
            self._thread = None
        if self._job_error:
            raise self._job_error  # pylint: disable=raising-bad-type

    @property
    def calibration_data(self):
        """Calibration data"""
        if self._calibration_data is None and self._thread is None:
            raise M3Error("Calibration is not calibrated")
        return self._calibration_data

    @property
    def timestamp(self):
        """Timestamp of calibration job

        Time is stored as UTC but returned in local time

        Returns:
            datetime: Timestamp in local time
        """
        if self._timestamp is None:
            return self._timestamp
        return self._timestamp.astimezone(tz.tzlocal())

    @calibration_data.setter
    def calibration_data(self, cals):
        if self._calibration_data is not None:
            raise M3Error("Calibration is already calibrated")
        self._calibration_data = cals

    def calibration_circuits(self):
        """Calibration circuits from underlying generator

        Returns:
            list: Calibration circuits
        """
        out_circuits = []
        creg_length = self.generator.num_qubits
        # need to do things different for the independent generator
        if self.generator.name == "independent":
            for string in self.generator:
                for idx, val in enumerate(string[::-1]):
                    if val:
                        # Prep and meas zero on qubit
                        qc = QuantumCircuit(self.backend_info["num_qubits"], 1)
                        qc.measure(self.bit_to_physical_mapping[idx], 0)
                        out_circuits.append(qc)
                        # Prep and meas one on qubit
                        qc = QuantumCircuit(self.backend_info["num_qubits"], 1)
                        qc.x(self.bit_to_physical_mapping[idx])
                        qc.measure(self.bit_to_physical_mapping[idx], 0)
                        out_circuits.append(qc)
                        break
        else:
            for string in self.generator:
                qc = QuantumCircuit(self.backend_info["num_qubits"], creg_length)
                for idx, val in enumerate(string[::-1]):
                    if val:
                        qc.x(self.bit_to_physical_mapping[idx])
                    qc.measure(self.bit_to_physical_mapping[idx], idx)
                out_circuits.append(qc)
        return out_circuits

    def calibrate_from_backend(self, shots=int(1e4), async_cal=True, overwrite=False):
        """Calibrate from the target backend using the generator circuits

        Parameters:
            shots (int): Number of shots defining the precision of
                         the underlying error elements
            async_cal (bool): Perform calibration asyncronously, default=True
            overwrite (bool): Overwrite a previous calibration, default=False

        Raises:
            M3Error: Calibration is already calibrated and overwrite=False
        """
        if self._calibration_data is not None and (not overwrite):
            M3Error("Calibration is already calibrated and overwrite=False")
        self._calibration_data = None
        cal_circuits = self.calibration_circuits()
        self._job_error = None
        if self.generator.name == 'independent':
            self.shots_per_circuit = shots
        else:
            self.shots_per_circuit = int(-(-shots // (self.generator.length / 2)))
        cal_job = self.backend.run(cal_circuits, shots=self.shots_per_circuit)
        self.job_id = cal_job.job_id()
        if async_cal:
            thread = threading.Thread(
                target=_job_thread,
                args=(cal_job, self),
            )
            self._thread = thread
            self._thread.start()
        else:
            _job_thread(cal_job, self)


def _job_thread(job, cal):
    """Process job result async"""
    try:
        res = job.result()
    # pylint: disable=broad-except
    except Exception as error:
        cal._job_error = error
        return
    else:
        cal.calibration_data = res.get_counts()
        timestamp = res.date
        # Needed since Aer result date is str but IBMQ job is datetime
        if isinstance(timestamp, datetime.datetime):
            timestamp = timestamp.isoformat()
        # Go to UTC times because we are going to use this for
        # resultsDB storage as well
        dt = datetime.datetime.fromisoformat(timestamp)
        dt_utc = dt.astimezone(datetime.timezone.utc)
        cal._timestamp = dt_utc
