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
"""
Calibration utility functions
-----------------------------

.. autosummary::
   :toctree: ../stubs/

   m3_legacy_cals

"""
import numpy as np


def m3_legacy_cals(m3_cals, calibration):
    """Convert new M3 calibration (flat array of diagonals)
    to the old list format of full matrices

    Parameters:
        m3_cals (ndarray): Array of single-qubit A-matrices (diagonals only)
        calibration (Calibration): A Calibration object

    Returns:
        list: Single-qubit A-matrices where index labels the physical qubit
    """
    num_qubits = calibration.backend_info['num_qubits']
    out_cals = [None] * num_qubits
    for bit, qubit in calibration.bit_to_physical_mapping.items():
        A = np.zeros((2, 2), dtype=float)
        A[0, 0] = m3_cals[2*bit]
        A[1, 1] = m3_cals[2*bit+1]
        A[1, 0] = 1 - A[0, 0]
        A[0, 1] = 1 - A[1, 1]
        out_cals[qubit] = A

    return out_cals
