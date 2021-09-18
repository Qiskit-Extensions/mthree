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

"""Test QuantumCircuit final measurement mapping"""
from qiskit import QuantumCircuit, transpile
from qiskit.test.mock.backends import FakeCasablanca
import mthree
from mthree.utils import final_measurement_mapping


def test_cals_mappings():
    """Test that mappings work in cals"""
    qc = QuantumCircuit(5, 4)
    qc.reset(range(5))
    qc.x(4)
    qc.h(range(5))
    qc.cx(range(4), 4)
    qc.draw()
    qc.h(range(4))
    qc.barrier()
    qc.measure(range(4), range(4))

    backend = FakeCasablanca()
    circs = transpile([qc]*5, backend)
    maps = final_measurement_mapping(circs)

    qubits = []
    for item in maps:
        qubits.extend(list(item))
    qubits = list(set(qubits))

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(maps)
    for qu in qubits:
        assert mit.single_qubit_cals[qu] is not None
