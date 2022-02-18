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
    # Generic Z on PROBS
    assert np.allclose(exp_val(PROBS, 'ZZZZ'), 0.7554)


def test_asym_operators():
    """Test that asym exp values work"""
    assert np.allclose(exp_val(PROBS, '0III'), 0.5318)
    assert np.allclose(exp_val(PROBS, 'III0'), 0.5285)
    assert np.allclose(exp_val(PROBS, '1011'), 0.0211)


PROBS = {'1000': 0.0022,
         '1001': 0.0045,
         '1110': 0.0081,
         '0001': 0.0036,
         '0010': 0.0319,
         '0101': 0.001,
         '1100': 0.0008,
         '1010': 0.0009,
         '1111': 0.3951,
         '0011': 0.0007,
         '0111': 0.01,
         '0000': 0.4666,
         '1101': 0.0355,
         '1011': 0.0211,
         '0110': 0.0081,
         '0100': 0.0099
         }
