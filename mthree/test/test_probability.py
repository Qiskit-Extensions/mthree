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

"""Test conversion to probability distribution"""
import numpy as np
from mthree.classes import QuasiDistribution


def test_known_conversion():
    """Reproduce conversion from Smolin PRL"""
    qprobs = {'0': 3/5, '1': 1/2, '2': 7/20, '3': 1/10, '4': -11/20}
    closest, dist = QuasiDistribution(qprobs, shots=1).nearest_probability_distribution(
        return_distance=True)
    ans = {'0': 9/20, '1': 7/20, '2': 1/5}

    for key, val in closest.items():
        assert abs(ans[key] - val) < 1e-14

    assert abs(dist-np.sqrt(0.38)) < 1e-14
