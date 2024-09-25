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

"""Test multiple job submission"""
from qiskit_ibm_runtime.fake_provider import FakeKolkataV2 as FakeKolkata
import mthree


def test_multiple_job_submission():
    """Test that submitting multiple jobs works"""
    backend = FakeKolkata()
    backend._conf_dict["max_experiments"] = 5
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    assert all(cal.trace() > 1.8 for cal in mit.single_qubit_cals)


def test_multiple_job_submission_single_circuit():
    """Test that submitting multiple single-circuit jobs works"""
    backend = FakeKolkata()
    backend._conf_dict["max_experiments"] = 5
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    assert all(cal.trace() > 1.8 for cal in mit.single_qubit_cals)
