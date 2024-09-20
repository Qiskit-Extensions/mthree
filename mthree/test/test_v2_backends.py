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
# pylint: disable=no-name-in-module

"""Test matrix elements"""
from qiskit_ibm_runtime.fake_provider import FakeAthensV2
import mthree


def test_v2_fake_backend():
    """Test that fake v2 backends work"""
    backend = FakeAthensV2()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    assert mit.cal_method == "independent"
