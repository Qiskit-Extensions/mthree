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
import pytest
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime.fake_provider import FakeCasablancaV2 as FakeCasablanca
import mthree
from mthree.exceptions import M3Error
from mthree.utils import final_measurement_mapping


def test_test_call_cals_twice():
    """Test trying to cal when another is in progress raises"""
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
    circs = transpile([qc] * 5, backend)
    maps = final_measurement_mapping(circs)
    mit = mthree.M3Mitigation(backend)
    with pytest.raises(M3Error):
        mit.cals_from_system(maps, async_cal=True)
        mit.cals_from_system(maps, async_cal=True)

    with pytest.raises(M3Error):
        mit.cals_from_system(maps, async_cal=True)
        mit.cals_from_system(maps)

    # Test that I can save cals while in async mode
    with pytest.raises(M3Error):
        cal_file = "data_cal.json"
        mit.cals_from_system(maps, cals_file=cal_file, async_cal=True)
