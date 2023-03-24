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

"""Test Hamming distance truncation"""
import numpy as np

from qiskit.providers.fake_provider import FakeKolkata
import mthree


def test_hamming_equiv():
    """Test Hamming truncation is same for direct and iterative methods"""
    # This test is valid because for the direct method, we do not stop
    # when all the elements within the Hamming distance are found, i.e
    # we check them all since the problem size is small.  However, for
    # the iterative method, we explicitly compute the number of terms
    # and break when we hit that number.  Thus, this test validates
    # that break via the computed column norms
    backend = FakeKolkata()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    for kk in range(8+1):
        _, details = mit.apply_correction(COUNTS, list(range(8)),
                                          details=True,
                                          method='iterative',
                                          distance=kk)
        _, details2 = mit.apply_correction(COUNTS, list(range(8)),
                                           details=True,
                                           method='direct',
                                           distance=kk)

        assert np.linalg.norm(details2['col_norms']-details['col_norms']) < 1e-15


COUNTS = {'11100010': 591,
          '01010111': 119,
          '10101101': 758,
          '00101011': 488,
          '10010001': 291,
          '01100011': 622,
          '10111000': 421,
          '11100000': 1226,
          '11100101': 957,
          '11111100': 261,
          '11101010': 482,
          '01000100': 385,
          '11111101': 281,
          '10101000': 1094,
          '00000010': 286,
          '01101010': 455,
          '11000100': 376,
          '01110011': 369,
          '00001000': 565,
          '00010001': 296,
          '01101111': 295,
          '01000000': 718,
          '01010100': 147,
          '00101110': 230,
          '10101110': 255,
          '00010011': 197,
          '00100001': 1536,
          '01000001': 939,
          '10001001': 682,
          '00100000': 1142,
          '11111111': 182,
          '00101001': 1389,
          '01100010': 575,
          '01100001': 1603,
          '11001010': 275,
          '11110000': 472,
          '11101001': 1532,
          '00100101': 896,
          '10100101': 917,
          '01110000': 441,
          '00000101': 429,
          '10110011': 369,
          '11110011': 366,
          '01110111': 151,
          '10000010': 278,
          '11100001': 1662,
          '11011011': 205,
          '01110101': 306,
          '01111101': 225,
          '00110111': 147,
          '10110010': 223,
          '00111010': 184,
          '11000001': 995,
          '11111001': 527,
          '11000000': 754,
          '10101001': 1492,
          '01100110': 257,
          '01101000': 1051,
          '01011000': 232,
          '11010011': 216,
          '00000011': 330,
          '00101101': 772,
          '01100000': 1257,
          '00101111': 248}
