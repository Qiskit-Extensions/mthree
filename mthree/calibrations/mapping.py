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
"""Calibration bit-mapping"""
import warnings

from mthree.exceptions import M3Error
from mthree._helpers import system_info


def calibration_mapping(backend, qubits=None):
    """Computes the bit to physical qubit mapping
    for a calibration over a given set of qubits

    Parameters:
        backend (Backend): A backend instance
        qubits (list): Qubits to calibrate over, default=None is all

    Returns:
        dict: Bit to physical qubit mapping

    Raises:
        M3Error: Duplicate qubit indices
    """
    backend_info = system_info(backend)
    if qubits is None:
        qubits = range(backend_info["num_qubits"])
        # Remove faulty qubits if any
        if any(backend_info["inoperable_qubits"]):
            qubits = list(
                filter(
                    lambda item: item not in backend_info["inoperable_qubits"],
                    list(range(backend_info["num_qubits"])),
                )
            )
            warnings.warn(
                "Backend reporting inoperable qubits."
                + " Skipping calibrations for: {}".format(
                    backend_info["inoperable_qubits"]
                )
            )
        num_qubits = len(qubits)
        bit_to_phyical_mapping = dict(zip(range(num_qubits), qubits))
    else:
        if len(set(qubits)) != len(qubits):
            raise M3Error("Duplicate qubit indices")
        num_qubits = len(qubits)
        bit_to_phyical_mapping = dict(zip(range(num_qubits), qubits))
    return bit_to_phyical_mapping
