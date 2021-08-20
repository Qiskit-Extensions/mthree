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
"""
Utility functions
-----------------

.. autosummary::
   :toctree: ../stubs/

   final_measurement_mapping

"""
import numpy as np
from mthree.classes import QuasiDistribution


def final_measurement_mapping(circuit):
    """Return the final measurement mapping for the circuit.

    Dict keys label measured qubits, whereas the values indicate the
    classical bit onto which that qubits measurement result is stored.

    Parameters:
        circuit (QuantumCircuit): Input Qiskit QuantumCircuit.

    Returns:
        dict: Mapping of qubits to classical bits for final measurements.
    """
    active_qubits = list(range(circuit.num_qubits))
    active_cbits = list(range(circuit.num_clbits))

    # Map registers to ints
    qint_map = {}
    for idx, qq in enumerate(circuit.qubits):
        qint_map[qq] = idx

    cint_map = {}
    for idx, qq in enumerate(circuit.clbits):
        cint_map[qq] = idx

    # Find final measurements starting in back
    qmap = []
    cmap = []
    for item in circuit._data[::-1]:
        if item[0].name == "measure":
            cbit = cint_map[item[2][0]]
            qbit = qint_map[item[1][0]]
            if cbit in active_cbits and qbit in active_qubits:
                qmap.append(qbit)
                cmap.append(cbit)
                active_cbits.remove(cbit)
                active_qubits.remove(qbit)
        elif item[0].name != "barrier":
            for qq in item[1]:
                _temp_qubit = qint_map[qq]
                if _temp_qubit in active_qubits:
                    active_qubits.remove(_temp_qubit)

        if not active_cbits or not active_qubits:
            break
    mapping = {}
    if cmap and qmap:
        for idx, qubit in enumerate(qmap):
            mapping[qubit] = cmap[idx]

    # Sort so that classical bits are in numeric order low->high.
    mapping = dict(sorted(mapping.items(), key=lambda item: item[1]))
    return mapping


def counts_to_vector(counts):
    """ Return probability vector from counts dict.

    Parameters:
        counts (dict): Input dict of counts.

    Returns:
        ndarray: 1D array of probabilities.
    """
    num_bitstrings = len(counts)
    shots = sum(counts.values())
    vec = np.zeros(num_bitstrings, dtype=float)
    idx = 0
    for val in counts.values():
        vec[idx] = val / shots
        idx += 1
    return vec


def vector_to_quasiprobs(vec, counts):
    """ Return dict of quasi-probabilities.

    Parameters:
        vec (ndarray): 1d vector of quasi-probabilites.
        counts (dict): Dict of counts

    Returns:
        QuasiDistribution: dict of quasi-probabilities
    """
    out_counts = {}
    idx = 0
    for key in counts:
        out_counts[key] = vec[idx]
        idx += 1
    return QuasiDistribution(out_counts)
