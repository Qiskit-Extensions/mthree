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
# pylint: disable=no-name-in-module

"""Test the converters"""
import numpy as np
from mthree.hamming import hamming_ball
from .column_testing import _test_vector_column_norm


mats = [np.array([[0.9954, 0.0682],
                  [0.0046, 0.9318]]),
        np.array([[0.9494, 0.1236],
                  [0.0506, 0.8764]]),
        np.array([[0.9778, 0.04],
                  [0.0222, 0.96]]),
        np.array([[0.9718, 0.0726],
                  [0.0282, 0.9274]]),
        np.array([[0.9832, 0.0568],
                  [0.0168, 0.9432]])]

cals = np.array([0.9832, 0.0568, 0.0168, 0.9432, 0.9718, 0.0726, 0.0282, 0.9274,
                0.9778, 0.04, 0.0222, 0.96, 0.9494, 0.1236, 0.0506, 0.8764,
                0.9954, 0.0682, 0.0046, 0.9318])

FULL_MAT = np.kron(mats[1], mats[0])
for ll in range(2, len(mats)):
    FULL_MAT = np.kron(mats[ll], FULL_MAT)


def test_vector_colnorm_d0():
    """Distance 0 vector col_norm gives diagonal elements"""

    counts = {}
    for kk in range(32):
        counts[bin(kk)[2:].zfill(5)] = 1/32

    out = _test_vector_column_norm(counts, cals, 0)

    for kk in range(32):
        assert abs(out[kk] - FULL_MAT[kk, kk]) < 1e-15


def test_vector_colnorm_d3():
    """Distance 3 vector col_norm verification"""

    counts = {}
    for kk in range(32):
        counts[bin(kk)[2:].zfill(5)] = 1/32

    out = _test_vector_column_norm(counts, cals, 3)

    for kk in range(32):
        arr = np.fromiter(bin(kk)[2:].zfill(5), np.uint8)
        elems = hamming_ball(arr, 0, 3)
        rows = np.asarray([np.sum(bits*2**np.arange(5)[::-1]) for bits in elems])
        assert abs(out[kk] - np.sum(FULL_MAT[rows, kk])) < 1e-15


def test_vector_colnorm_d5():
    """Distance 5 vector col_norm gives unit norm for 5Q matrix"""

    counts = {}
    for kk in range(32):
        counts[bin(kk)[2:].zfill(5)] = 1/32

    out = _test_vector_column_norm(counts, cals, 5)

    for kk in range(32):
        assert abs(out[kk] - 1) < 1e-15
