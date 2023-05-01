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
"""Test bit-array generators"""
import numpy as np

from mthree.generators import IndependentGenerator, RandomGenerator


def test_random1():
    """Test random generator setting num_arrays works"""
    gen1 = RandomGenerator(5, 1)
    assert len(gen1.all_calibration_arrays()) == 1

    gen127 = RandomGenerator(50, 127)
    assert len(gen127.all_calibration_arrays()) == 127

    gen433 = RandomGenerator(433, 433)
    assert len(gen433.all_calibration_arrays()) == 433


def test_random2():
    """Test random generator can be called twice"""
    gen = RandomGenerator(7, 7)
    out1 = [item for item in gen]
    out2 = [item for item in gen]
    assert len(out1) == 7
    assert len(out2) == 7
    for kk in range(7):
        assert np.allclose(out1[kk], out2[kk])


def test_random3():
    """Test random generator seeding works"""
    gen1 = RandomGenerator(7, 8, seed=12345)
    gen2 = RandomGenerator(7, 8, seed=12345)
    out1 = [item for item in gen1]
    out2 = [item for item in gen2]
    for kk in range(8):
        assert np.allclose(out1[kk], out2[kk])


def test_independent1():
    """Test independent generator setting num_arrays works"""
    gen1 = IndependentGenerator(5)
    assert len(gen1.all_calibration_arrays()) == 5

    gen50 = IndependentGenerator(50)
    assert len(gen50.all_calibration_arrays()) == 50

    gen433 = IndependentGenerator(433)
    assert len(gen433.all_calibration_arrays()) == 433


def test_independent2():
    """Test independent generator can be called twice"""
    gen = IndependentGenerator(77)
    out1 = [item for item in gen]
    out2 = [item for item in gen]
    assert len(out1) == 77
    assert len(out2) == 77
    for kk in range(77):
        assert np.allclose(out1[kk], out2[kk])


def test_independent3():
    """Test independent generator returns correct bit-arrays"""
    num_qubits = 5
    for idx, arr in enumerate(IndependentGenerator(num_qubits)):
        # Since 0th qubit is right-most bit
        assert np.where(arr == 1)[0][0] == num_qubits-idx-1
