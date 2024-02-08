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

"""Test inoperable qubits"""
import pytest
from qiskit_ibm_runtime.fake_provider import FakeKolkata
import mthree


def _faulty():
    return [1, 3, 5, 7]


BACKEND = FakeKolkata()
_ = BACKEND.properties()
BACKEND._properties.faulty_qubits = _faulty


def test_inoperable_qubits1():
    """Test that inoperable qubits are ignored"""
    mit = mthree.M3Mitigation(BACKEND)
    mit.cals_from_system()
    for qubit in _faulty():
        assert mit.single_qubit_cals[qubit] is None


def test_inoperable_qubits2():
    """Test that explicitly using inoperable qubits raises error"""
    mit = mthree.M3Mitigation(BACKEND)
    with pytest.raises(mthree.exceptions.M3Error):
        mit.cals_from_system([0, 3])
