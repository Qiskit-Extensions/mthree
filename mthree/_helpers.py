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
"""
Helper functions
"""
from qiskit.providers import BackendV2
from qiskit_ibm_runtime import IBMBackend
from mthree.exceptions import M3Error


def system_info(backend):
    """Return backend information needed by M3.

    Parameters:
        backend (BackendV1 or BackendV2): A Qiskit backend

    Returns:
        dict: Backend information
    """
    info_dict = {}
    info_dict["inoperable_qubits"] = []
    config = backend.configuration()
    info_dict["name"] = backend.name
    info_dict["num_qubits"] = config.num_qubits
    _max_shots = backend.configuration().max_shots
    info_dict["max_shots"] = _max_shots if _max_shots else int(1e6)

    if isinstance(backend, IBMBackend):
        info_dict["simulator"] = False
    elif isinstance(backend, BackendV2):
        info_dict["simulator"] = True
    else:
        raise M3Error("Invalid backend passed.")
    # Look for faulty qubits.  Renaming to 'inoperable' here
    if hasattr(backend, "properties"):
        if hasattr(backend.properties(), "faulty_qubits"):
            info_dict["inoperable_qubits"] = backend.properties().faulty_qubits()
    return info_dict
