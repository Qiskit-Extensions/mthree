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
from qiskit.test.mock import FakeMontreal
import mthree


def test_quasi_attr_set():
    """Test quasi-probs attributes are set"""
    backend = FakeMontreal()

    N = 6
    qc = QuantumCircuit(N)
    qc.x(range(0, N))
    qc.h(range(0, N))
    for kk in range(N//2, 0, -1):
        qc.ch(kk, kk-1)
    for kk in range(N//2, N-1):
        qc.ch(kk, kk+1)
    qc.measure_all()

    qubits = [1, 4, 7, 10, 12, 13]

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(qubits)

    raw_counts = execute(qc, backend, shots=1024,
                         initial_layout=qubits).result().get_counts()
    quasi1 = mit.apply_correction(raw_counts, qubits,
                                  return_mitigation_overhead=True, method='direct')
    quasi2 = mit.apply_correction(raw_counts, qubits,
                                  return_mitigation_overhead=True, method='iterative')

    quasi3 = mit.apply_correction(raw_counts, qubits,
                                  return_mitigation_overhead=False, method='direct')
    quasi4 = mit.apply_correction(raw_counts, qubits,
                                  return_mitigation_overhead=False, method='iterative')

    shots = 1024
    assert quasi1.shots == shots
    assert quasi2.shots == shots
    assert quasi3.shots == shots
    assert quasi4.shots == shots

    assert quasi1.mitigation_overhead is not None
    assert quasi2.mitigation_overhead is not None
    assert quasi3.mitigation_overhead is None
    assert quasi4.mitigation_overhead is None
