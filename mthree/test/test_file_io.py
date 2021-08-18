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

"""Test cals file IO"""
import numpy as np
from qiskit import QuantumCircuit, execute
from qiskit.test.mock import FakeAthens
import mthree


def test_load_cals_from_file():
    """Check the cals can be loaded from a saved file"""
    backend = FakeAthens()

    qc = QuantumCircuit(5)
    qc.h(2)
    qc.cx(2, 1)
    qc.cx(2, 3)
    qc.cx(1, 0)
    qc.cx(3, 4)
    qc.measure_all()

    raw_counts = execute(qc, backend).result().get_counts()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(cals_file='cals.json')

    mit2 = mthree.M3Mitigation()
    mit2.cals_from_file(cals_file='cals.json')

    assert len(mit.single_qubit_cals) == len(mit2.single_qubit_cals)

    # check that cals are identical
    for idx, item in enumerate(mit.single_qubit_cals):
        if item is None:
            assert mit2.single_qubit_cals[idx] is None
        else:
            assert np.allclose(item, mit2.single_qubit_cals[idx])

    mit2_counts = mit.apply_correction(raw_counts, qubits=range(5))
    assert mit2_counts is not None
