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

"""Test is various methods agree"""

import numpy as np
from qiskit import QuantumCircuit, execute
from qiskit.test.mock import FakeAthens
import mthree


def test_methods_equality():
    """Make sure direct and iterative solvers agree with each other."""
    qc = QuantumCircuit(5)
    qc.h(2)
    qc.cx(2, 1)
    qc.cx(1, 0)
    qc.cx(2, 3)
    qc.cx(3, 4)
    qc.measure_all()

    backend = FakeAthens()
    raw_counts = execute(qc, backend, shots=2048).result().get_counts()

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()

    iter_q = mit.apply_correction(raw_counts, range(5), method='iterative')
    direct_q = mit.apply_correction(raw_counts, range(5), method='direct')

    for key, val in direct_q.items():
        assert key in iter_q.keys()
        assert np.abs(val-iter_q[key]) < 1e-5


def test_set_iterative():
    """Make sure can overload auto setting"""
    qc = QuantumCircuit(5)
    qc.h(2)
    qc.cx(2, 1)
    qc.cx(1, 0)
    qc.cx(2, 3)
    qc.cx(3, 4)
    qc.measure_all()

    backend = FakeAthens()
    raw_counts = execute(qc, backend, shots=4096).result().get_counts()

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(shots=4096)

    _, details = mit.apply_correction(raw_counts, range(5),
                                      method='iterative',
                                      details=True)
    assert details['method'] == 'iterative'

    _, details = mit.apply_correction(raw_counts, range(5),
                                      details=True)
    assert details['method'] == 'direct'
