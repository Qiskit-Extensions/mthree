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
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from qiskit.test.mock.backends import FakeCasablanca
from mthree.utils import final_measurement_mapping


def test_empty_circ():
    """Empty circuit has no mapping"""
    qc = QuantumCircuit()
    assert final_measurement_mapping(qc) == {}


def test_simple_circ():
    """Just measures"""
    qc = QuantumCircuit(5)
    qc.measure_all()
    assert final_measurement_mapping(qc) == {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}


def test_simple2_circ():
    """Meas followed by Hadamards"""
    qc = QuantumCircuit(5)
    qc.measure_all()
    qc.h(range(5))
    assert final_measurement_mapping(qc) == {}


def test_multi_qreg():
    """Test multiple qregs"""
    qr1 = QuantumRegister(2, "q1")
    qr2 = QuantumRegister(3, "q2")
    cr = ClassicalRegister(5)
    qc = QuantumCircuit(qr1, qr2, cr)

    qc.h(range(5))
    qc.measure(0, 0)
    qc.h(range(5))
    qc.measure(range(2, 4), range(2, 4))
    qc.barrier(range(5))
    qc.measure(1, 4)
    assert final_measurement_mapping(qc) == {2: 2, 3: 3, 1: 4}


def test_multi_creg():
    """Test multiple qregs"""
    qr1 = QuantumRegister(2, "q1")
    qr2 = QuantumRegister(3, "q2")
    cr1 = ClassicalRegister(3, "c1")
    cr2 = ClassicalRegister(2, "c2")
    qc = QuantumCircuit(qr1, qr2, cr1, cr2)

    qc.h(range(5))
    qc.measure(0, 0)
    qc.h(range(5))
    qc.measure(range(2, 4), range(2, 4))
    qc.barrier(range(5))
    qc.measure(1, 4)
    assert final_measurement_mapping(qc) == {2: 2, 3: 3, 1: 4}


def test_mapping_list():
    """Test that final mapping works for list input"""
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
    assert len(maps) == 5

    maps = final_measurement_mapping(qc)
    assert not isinstance(maps, list)
