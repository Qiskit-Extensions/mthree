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
   expval
   stddev
   expval_and_stddev
   marginal_distribution

"""
import numpy as np

from qiskit.result import marginal_distribution as marg_dist
from mthree.exceptions import M3Error
from mthree.classes import (
    QuasiDistribution,
    ProbDistribution,
    QuasiCollection,
    ProbCollection,
)


def final_measurement_mapping(circuit):
    """Return the final measurement mapping for the circuit.

    Dict keys label measured qubits, whereas the values indicate the
    classical bit onto which that qubits measurement result is stored.

    Parameters:
        circuit (QuantumCircuit or list): Input Qiskit QuantumCircuit or circuits.

    Returns:
        dict or list: Mapping of classical bits to qubits for final measurements.
    """
    given_list = False
    if isinstance(circuit, (list, np.ndarray)):
        given_list = True
    if not given_list:
        circuit = [circuit]

    maps_out = [_final_measurement_mapping(circ) for circ in circuit]

    if not given_list:
        return maps_out[0]
    return maps_out


def marginal_distribution(dist, indices, mapping=None):
    """Grab the marginal counts from a given distribution.

    If an operator is passed for the `indices` then the position of the
    non-identity elements in the string will be used to set the indices
    to marginalize over.

    The mapping passed will be marginalized so that it can be directly
    used in applying the correction.  The type of mapping at output is
    the same as that input.

    Parameters:
        dist (dict): Input distribution
        indices (array_like or str): Indices (qubits) to keep or operator string
        mapping (dict or array_like): Optional, final measurement mapping.

    Returns:
        dict: Marginal distribution
        list or dict: The reduced mapping if an optional mapping (list or dict) is given

    Raises:
        M3Error: Operator length does not equal bit-string length
        M3Error: One or more indices is out of bounds
    """
    key_len = len(next(iter(dist)))
    if isinstance(indices, str):
        indices = indices.upper()
        if len(indices) != key_len:
            raise M3Error(
                "Operator length does not equal distribution bit-string length."
            )
        indices = [
            (key_len - kk - 1)
            for kk in range(key_len - 1, -1, -1)
            if indices[kk] != "I"
        ]

    out_dist = marg_dist(dist, indices)

    if mapping:
        if isinstance(mapping, list):
            out_mapping = [mapping[kk] for kk in indices]
        else:
            # mapping is a dict
            out_mapping = {}
            for idx, ind in enumerate(indices):
                out_mapping[idx] = mapping[ind]
        return out_dist, out_mapping
    return out_dist


def _final_measurement_mapping(circuit):
    """Return the measurement mapping for the circuit.

    Dict keys label classical bits, whereas the values indicate the
    physical qubits that are measured to produce those bit values.

    Parameters:
        circuit (QuantumCircuit): Input Qiskit QuantumCircuit.

    Returns:
        dict: Mapping of classical bits to qubits for final measurements.
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

        if not active_cbits or not active_qubits:
            break
    mapping = {}
    if cmap and qmap:
        for idx, qubit in enumerate(qmap):
            mapping[cmap[idx]] = qubit

    # Sort so that classical bits are in numeric order low->high.
    mapping = dict(sorted(mapping.items(), key=lambda item: item[0]))
    return mapping


def _expval_std(items, exp_ops="", method=0):
    """Compute expectation values from distributions.

    Parameters:
       items (list or dict or Counts or ProbDistribution or QuasiDistribution): Input
            distributions.

       exp_ops (str or dict or list): String or dict representation of diagonal qubit
                                      operators used in computing the expectation value.

        method (int): 0=expvals, 1=stddev, 2=expval and stddev.

    Returns:
        float : Expectation value.
        tuple: Expectation value and stddev.
        ndarray: Array of expectation values or stddev
        list: List of expvals and stddev tuples.

    Raises:
        M3Error: Not a valid method.
    """
    if method not in [0, 1, 2]:
        raise M3Error("Invalid method int {} passed.".format(method))

    got_list = False
    if isinstance(items, list):
        got_list = True
    else:
        items = [items]

    if isinstance(exp_ops, list):
        if not len(exp_ops) == len(items):
            raise M3Error(
                (
                    "exp_ops length ({}) does not match number "
                    + "of items passed ({})."
                ).format(len(exp_ops), len(items))
            )
    else:
        exp_ops = [exp_ops] * len(items)

    if isinstance(items[0], (ProbCollection, QuasiCollection)):
        if method == 0:
            out = items.expval(exp_ops)
        elif method == 1:
            out = items.stddev()
        else:
            out = items.expval_and_stddev(exp_ops)
    elif not isinstance(items[0], (ProbDistribution, QuasiDistribution)):
        out = []
        if method == 0:
            for idx, it in enumerate(items):
                out.append(ProbDistribution(it).expval(exp_ops[idx]))
            out = np.asarray(out, dtype=np.float32)
        elif method == 1:
            for _, it in enumerate(items):
                out.append(ProbDistribution(it).stddev())
            out = np.asarray(out, dtype=np.float32)
        else:
            for idx, it in enumerate(items):
                out.append(ProbDistribution(it).expval_and_stddev(exp_ops[idx]))
    else:
        out = []
        if method == 0:
            for idx, it in enumerate(items):
                out.append(it.expval(exp_ops[idx]))
            out = np.asarray(out, dtype=np.float32)
        elif method == 1:
            for _, it in enumerate(items):
                out.append(it.stddev())
            out = np.asarray(out, dtype=float)
        else:
            for idx, it in enumerate(items):
                out.append(it.expval_and_stddev(exp_ops[idx]))

    if not got_list:
        return out[0]
    return out


def expval(items, exp_ops=""):
    """Compute expectation values from distributions.

    .. versionadded:: 0.16.0

        Parameters:
           items (list or dict or Counts or ProbDistribution or QuasiDistribution): Input
                distributions.

           exp_ops (str or dict or list): String or dict representation of diagonal
                                          qubit operators used in computing the expectation
                                          value.

        Returns:
            float : Expectation value.
            ndarray: Array of expectation values

        Notes:
            Cannot mix Counts and dicts with M3 Distributions in the same call.

            The dict operator format is a sparse diagonal format
            using bitstrings as the keys.
    """
    return _expval_std(items, exp_ops=exp_ops, method=0)


def stddev(items):
    """Compute expectation values from distributions.

    .. versionadded:: 0.16.0

        Parameters:
           items (list or dict or Counts or ProbDistribution or QuasiDistribution): Input
                distributions.

        Returns:
            float : Expectation value.
            ndarray: Array of expectation values

        Notes:
            Cannot mix Counts and dicts with M3 Distributions in the same call.
    """
    return _expval_std(items, method=1)


def expval_and_stddev(items, exp_ops=""):
    """Compute expectation values from distributions.

    .. versionadded:: 0.16.0

        Parameters:
           items (list or dict or Counts or ProbDistribution or QuasiDistribution): Input
                distributions.

           exp_ops (str or dict or list): String or dict representation of diagonal qubit
                                          operators used in computing the expectation value.

        Returns:
            float : Expectation value.
            ndarray: Array of expectation values

        Notes:
            Cannot mix Counts and dicts with M3 Distributions in the same call.

            The dict operator format is a sparse diagonal format
            using bitstrings as the keys.
    """
    return _expval_std(items, exp_ops=exp_ops, method=2)


def counts_to_vector(counts):
    """Return probability vector from counts dict.

    Parameters:
        counts (dict): Input dict of counts.

    Returns:
        ndarray: 1D array of probabilities.
    """
    num_bitstrings = len(counts)
    shots = sum(counts.values())
    vec = np.zeros(num_bitstrings, dtype=np.float32)
    idx = 0
    for val in counts.values():
        vec[idx] = val / shots
        idx += 1
    return vec


def vector_to_quasiprobs(vec, counts):
    """Return dict of quasi-probabilities.

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
