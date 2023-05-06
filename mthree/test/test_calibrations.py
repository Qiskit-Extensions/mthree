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
"""Test Calibration class"""
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import FakeManila

from mthree.generators import IndependentGenerator, HadamardGenerator
from mthree.calibrations import Calibration

BACKEND = FakeManila()


def test_independent_generator_circuits():
    """Test independent generator circuits get remapped correctly"""
    qubits = [0, 4, 2, 1, 3]
    cal = Calibration(BACKEND, qubits, IndependentGenerator(5))
    cal_circuits = cal.calibration_circuits()
    for idx, val in cal.bit_to_physical_mapping.items():
        qc = QuantumCircuit(5, 1)
        qc.x(val)
        qc.measure(val, 0)
        assert qc == cal_circuits[idx]


def test_hadamard_generator_circuits():
    """Test hadamard generator circuits get remapped correctly"""
    qubits = [4, 0, 1, 3, 2]
    gen = HadamardGenerator(5)
    cal = Calibration(BACKEND, qubits, gen)
    cal_circs = cal.calibration_circuits()
    for kk, string in enumerate(gen):
        string = string[::-1]
        qc = QuantumCircuit(5, 5)
        for idx, val in cal.bit_to_physical_mapping.items():
            if string[idx]:
                qc.x(val)
            qc.measure(val, idx)     
        assert qc == cal_circs[kk]
