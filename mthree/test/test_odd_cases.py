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

"""Test utils functions"""
from qiskit import Aer, QuantumCircuit, transpile
import mthree


def test_simulator_overhead():
    """Verify a single bitstring from the sim works with mitigation overhead"""
    qc = QuantumCircuit(6)
    qc.measure_all()

    backend = Aer.get_backend("aer_simulator")
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(range(6))

    trans_qc = transpile(qc, backend)
    raw_counts = backend.run(trans_qc, shots=100).result().get_counts()

    quasi = mit.apply_correction(raw_counts, range(6), return_mitigation_overhead=True)
    assert quasi.mitigation_overhead == 1.0
