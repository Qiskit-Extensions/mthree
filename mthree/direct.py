# This code is part of Mthree.
#
# (C) Copyright IBM 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=no-name-in-module, invalid-name
"""Direct solver routines"""
import scipy.linalg as la

from mthree.matrix import _reduced_cal_matrix
from mthree.utils import counts_to_vector, vector_to_quasiprobs
from mthree.norms import ainv_onenorm_est_lu
from mthree.exceptions import M3Error


def reduced_cal_matrix(mitigator, counts, qubits, distance=None):
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
        raise M3Error(
            "Bitstring length ({}) does not match".format(bitstring_len)
            + " number of qubits ({})".format(num_bits)
        )

    cals = mitigator._form_cals(qubits)
    A, counts, _ = _reduced_cal_matrix(counts, cals, num_bits, distance)
    return A, counts


def direct_solver(
    mitigator, counts, qubits, distance=None, return_mitigation_overhead=False
):
    """Apply the mitigation using direct LU factorization.

    Parameters:
        counts (dict): Input counts dict.
        qubits (int): Qubits over which to calibrate.
        distance (int): Distance to correct for. Default=num_bits
        return_mitigation_overhead (bool): Returns the mitigation overhead, default=False.

    Returns:
        QuasiDistribution: dict of Quasiprobabilites
    """
    cals = mitigator._form_cals(qubits)
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
