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

"""Test is various methods agree"""

import numpy as np
import mthree


def test_bad_A_matrix_sdd():
    """Test a bad A-matrix for SDD"""

    mit = mthree.M3Mitigation(None)
    mit.single_qubit_cals = BAD_CALS
    is_sdd = mit._check_sdd(COUNTS, range(5))
    assert not is_sdd


def test_goood_A_matrix_sdd():
    """Test a bad A-matrix for SDD"""

    mit = mthree.M3Mitigation(None)
    mit.single_qubit_cals = GOOD_CALS
    is_sdd = mit._check_sdd(COUNTS, range(5))
    assert is_sdd


BAD_CALS = [np.array([[0.99, 0.08288574],
                      [0.01, 0.91711426]]),
            np.array([[0.91967773, 0.14404297],
                      [0.08032227, 0.85595703]]),
            np.array([[0.9, 0.13195801],
                      [0.1, 0.86804199]]),
            np.array([[0.85, 0.0703125],
                      [0.15, 0.9296875]]),
            np.array([[0.9, 0.23425293],
                      [0.1, 0.76574707]])]

GOOD_CALS = [np.array([[1, 0.05419922],
                       [0, 0.94580078]]),
             np.array([[0.95532227, 0.06750488],
                       [0.04467773, 0.93249512]]),
             np.array([[0.99047852, 0.03967285],
                       [0.00952148, 0.96032715]]),
             np.array([[0.96643066, 0.09606934],
                       [0.03356934, 0.90393066]]),
             np.array([[0.99255371, 0.06066895],
                       [0.00744629, 0.93933105]])]

COUNTS = {'00000': 3591,
          '00001': 7,
          '10000': 77,
          '10001': 2,
          '10010': 2,
          '10011': 14,
          '10100': 5,
          '10101': 22,
          '10110': 29,
          '10111': 305,
          '11000': 17,
          '11001': 10,
          '11010': 8,
          '11011': 128,
          '11100': 69,
          '11101': 196,
          '11110': 199,
          '11111': 2734,
          '00010': 153,
          '00011': 40,
          '00100': 46,
          '00101': 6,
          '00110': 6,
          '00111': 72,
          '01000': 152,
          '01001': 1,
          '01010': 14,
          '01011': 12,
          '01100': 5,
          '01101': 22,
          '01110': 8,
          '01111': 240}
