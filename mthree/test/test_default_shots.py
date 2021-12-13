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

"""Test matrix elements"""
from qiskit import QuantumCircuit, execute
from qiskit.test.mock import FakeAthens
import mthree


LOW_SHOTS = 543
HIGH_SHOTS = 100000

def test_athens_mod_shots1():
    """Check that default shots works properly for low settings"""
    backend = FakeAthens()

    qc = QuantumCircuit(5)
    qc.h(2)
    qc.cx(2, 1)
    qc.cx(2, 3)
    qc.cx(1, 0)
    qc.cx(3, 4)
    qc.measure_all()

    backend._configuration.max_shots = LOW_SHOTS

    raw_counts = execute(qc, backend).result().get_counts()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    mit_counts = mit.apply_correction(raw_counts, qubits=range(5))

    assert mit_counts.shots == LOW_SHOTS

def test_athens_mod_shots2():
    """Check that default shots works properly for high settings"""
    backend = FakeAthens()

    qc = QuantumCircuit(5)
    qc.h(2)
    qc.cx(2, 1)
    qc.cx(2, 3)
    qc.cx(1, 0)
    qc.cx(3, 4)
    qc.measure_all()

    backend._configuration.max_shots = HIGH_SHOTS

    raw_counts = execute(qc, backend).result().get_counts()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    mit_counts = mit.apply_correction(raw_counts, qubits=range(5))

    assert mit_counts.shots == 10000
