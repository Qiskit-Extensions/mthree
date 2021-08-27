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

"""Test list inputs"""
import numpy as np
from mthree.expval import exp_val


def test_basic_expvals():
    """Test that basic exp values work"""
    # ZZ even GHZ is 1.0
    assert np.allclose(exp_val({'00': 0.5, '11': 0.5}), 1.0)
    # ZZ odd GHZ is 0.0
    assert np.allclose(exp_val({'000': 0.5, '111': 0.5}), 0.0)
    # All id ops goes to 1.0
    assert np.allclose(exp_val({'000': 0.5, '111': 0.5}, 'III'), 1.0)
    # flipping one to I makes even GHZ 0.0
    assert np.allclose(exp_val({'00': 0.5, '11': 0.5}, 'IZ'), 0.0)
    assert np.allclose(exp_val({'00': 0.5, '11': 0.5}, 'ZI'), 0.0)
