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

"""Test opertor groupings"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.test.mock import FakeGuadalupe
import mthree


def test_marginals1():
    """Test marginal indices return expected values
    """
    counts = {'011': 123, '111': 4554, '101': 180, '100': 21,
              '001': 72, '110': 114, '010': 30, '000': 4906}
    
    marginal_zero = mthree.utils.marginal_distribution(counts, [0])
    assert marginal_zero['0'] == 5071
    assert marginal_zero['1'] == 4929

    marginal_zero_two = mthree.utils.marginal_distribution(counts, [0, 2])
    assert marginal_zero_two['00'] == 4936
    assert marginal_zero_two['10'] == 135
    assert marginal_zero_two['01'] == 195
    assert marginal_zero_two['11'] == 4734

    marginal_two_zero = mthree.utils.marginal_distribution(counts, [2, 0])
    assert marginal_two_zero['00'] == marginal_zero_two['00']
    assert marginal_two_zero['10'] == marginal_zero_two['01']
    assert marginal_two_zero['01'] == marginal_zero_two['10']
    assert marginal_two_zero['11'] == marginal_zero_two['11']
