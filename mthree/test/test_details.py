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

"""Test details handling"""
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime.fake_provider import FakeAthensV2

import mthree


BACKEND = FakeAthensV2()


def test_details_one_circuit():
    """Test details work single circuit"""
    # Build circuit here
    N = 4
    qc = QuantumCircuit(N)

    qc.x(range(N))
    qc.h(range(N))

    for kk in range(N // 2, 0, -1):
        qc.ch(kk, kk - 1)
    for kk in range(N // 2, N - 1):
        qc.ch(kk, kk + 1)
    qc.measure_all()

    trans_qc = transpile(qc, BACKEND, optimization_level=3)
    mapping = mthree.utils.final_measurement_mapping(trans_qc)

    raw_counts = BACKEND.run(trans_qc, shots=int(1e4)).result().get_counts()

    mit = mthree.M3Mitigation(BACKEND)
    mit.cals_from_system()

    quasi, details = mit.apply_correction(raw_counts, mapping, details=True)

    assert isinstance(quasi, mthree.classes.QuasiDistribution)
    assert isinstance(details, dict)


def test_details_multi_circuit():
    """Test details work for multiple circuits"""
    # Build circuit here
    N = 4
    qc = QuantumCircuit(N)

    qc.x(range(N))
    qc.h(range(N))

    for kk in range(N // 2, 0, -1):
        qc.ch(kk, kk - 1)
    for kk in range(N // 2, N - 1):
        qc.ch(kk, kk + 1)
    qc.measure_all()

    trans_qc = transpile(qc, BACKEND, optimization_level=3)
    mapping = mthree.utils.final_measurement_mapping(trans_qc)

    raw_counts = BACKEND.run(trans_qc, shots=int(1e4)).result().get_counts()

    mit = mthree.M3Mitigation(BACKEND)
    mit.cals_from_system()

    quasi, details = mit.apply_correction([raw_counts] * 2, [mapping] * 2, details=True)

    assert isinstance(quasi, mthree.classes.QuasiCollection)
    assert isinstance(details, list)
    assert len(details) == 2
