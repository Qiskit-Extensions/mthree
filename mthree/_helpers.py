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
from qiskit.providers import BackendV1, BackendV2
from mthree.exceptions import M3Error


def system_info(backend):
    """Return backend information needed by M3.

    Parameters:
        backend (BackendV1 or BackendV2): A Qiskit backend

    Returns:
        dict: Backend information
    """
    info_dict = {}
    if isinstance(backend, BackendV1):
        config = backend.configuration()
        info_dict["name"] = backend.name()
        info_dict["num_qubits"] = config.num_qubits
        info_dict["max_shots"] = config.max_shots
        info_dict["simulator"] = config.simulator
        # A hack for Qiskit/Terra #9572
        if "fake" in info_dict["name"]:
            info_dict["simulator"] = True
    elif isinstance(backend, BackendV2):
        info_dict["name"] = backend.name
        info_dict["num_qubits"] = backend.num_qubits
        _max_shots = backend.options.validator.get("shots", (None, None))[1]
        info_dict["max_shots"] = _max_shots if _max_shots else int(1e9)
        # Default to simulator is True for safety
        info_dict["simulator"] = True
        # This is a V2 coming from IBM provider
        # No other way to tell outside of configuration
        # E.g. how to tell that ibmq_qasm_simulator is sim, but real devices not
        # outside of configuration?
        if hasattr(backend, 'configuration'):
            info_dict["simulator"] = backend.configuration().simulator
    else:
        raise M3Error('Invalid backend passed.')
    return info_dict
