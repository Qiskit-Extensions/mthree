# This code is part of Mthree.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=no-name-in-module

"""Test opertor groupings"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime.fake_provider import FakeAthensV2 as FakeAthens
import mthree


def test_groupings1():
    """Test grouping of operators output"""
    backend = FakeAthens()
    qc = QuantumCircuit(4)
    qc.h(0)
    qc.cx(0, range(1, 4))
    qc.measure_all()

    trans_circs = transpile(
        [qc] * 2, backend, optimization_level=3, approximation_degree=0
    )
    mappings = mthree.utils.final_measurement_mapping(trans_circs)

    job = backend.run(trans_circs, shots=10000)
    counts = job.result().get_counts()

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(mappings, shots=10000)

    quasis = mit.apply_correction(counts, mappings, return_mitigation_overhead=True)
    expvals = quasis.expval([["IIII", "ZZZZ", "0000", "1111"], ["IIII", "1111"]])

    assert expvals[0].shape[0] == 4
    assert np.allclose(expvals[0][0], 1)
    assert np.allclose(expvals[0][2], quasis[0]["0000"])
    assert np.allclose(expvals[0][3], quasis[0]["1111"])
    assert expvals[1].shape[0] == 2
    assert np.allclose(expvals[1][0], 1)
    assert np.allclose(expvals[1][1], quasis[1]["1111"])


def test_groupings2():
    """Check ordering of grouped outputs"""
    backend = FakeAthens()
    qc = QuantumCircuit(4)
    qc.h(0)
    qc.cx(0, range(1, 4))
    qc.measure_all()

    trans_circs = transpile(
        [qc] * 2, backend, optimization_level=3, approximation_degree=0
    )
    mappings = mthree.utils.final_measurement_mapping(trans_circs)

    job = backend.run(trans_circs, shots=10000)
    counts = job.result().get_counts()

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(mappings, shots=10000)

    quasis = mit.apply_correction(counts, mappings, return_mitigation_overhead=True)
    expvals = quasis.expval(["IIII", ["IIII", "1111"]])

    assert np.allclose(expvals[0], 1.0)
    assert expvals[1].shape[0] == 2

    probs = quasis.nearest_probability_distribution()
    expvals2 = probs.expval(["IIII", ["IIII", "1111"]])
    assert np.allclose(expvals2[0], 1.0)
    assert expvals2[1].shape[0] == 2
