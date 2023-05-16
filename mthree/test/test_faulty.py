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

"""Test faulty qubits handling"""
import numpy as np
import pytest

import mthree


def test_faulty_logic():
    """Test faulty qubits raise warning"""

    mit = mthree.M3Mitigation(None)
    mit.single_qubit_cals = [
        np.array([[0.9819, 0.043], [0.0181, 0.957]]),
        np.array([[0.4849, 0.5233], [0.5151, 0.4767]]),
        np.array([[0.9092, 0.4021], [0.0908, 0.5979]]),
        np.array([[0.4117, 0.8101], [0.5883, 0.1899]]),
    ]
    mit.faulty_qubits = [1, 3]
    counts = {"00": 0.4, "01": 0.1, "11": 0.5}
    with pytest.warns(UserWarning) as record:
        _ = mit.apply_correction(counts, qubits=[3, 2])

    assert len(record) == 1
    assert record[0].message.args[0] == "Using faulty qubits: {3}"


def test_faulty_io():
    """Check round-tripping IO still has faulty qubits"""
    mit = mthree.M3Mitigation(None)
    mit.single_qubit_cals = [
        np.array([[0.9819, 0.043], [0.0181, 0.957]]),
        np.array([[0.4849, 0.5233], [0.5151, 0.4767]]),
        np.array([[0.9092, 0.4021], [0.0908, 0.5979]]),
        np.array([[0.4117, 0.8101], [0.5883, 0.1899]]),
    ]
    mit.cals_to_file("bad_cals.json")
    mit2 = mthree.M3Mitigation(None)
    mit2.cals_from_file("bad_cals.json")
    assert mit2.faulty_qubits == [1, 3]
