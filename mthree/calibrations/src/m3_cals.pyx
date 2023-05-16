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
# cython: c_string_type=unicode, c_string_encoding=utf8

cimport cython
from libcpp.unordered_map cimport unordered_map as umap
from libcpp.string cimport string
from cython.operator cimport dereference, postincrement
from libcpp.pair cimport pair
from libcpp cimport bool
import numpy as np
cimport numpy as np


@cython.cdivision(True)
@cython.boundscheck(False)
def calibration_to_m3(list counts, object generator):
    """Conver raw calibration data into M3 calibration data

    Parameters:
        counts (list): List of counts dictionaries
        generator (Generator): Bit-string generator

    Returns:
        ndarray: Array of single qubit calibration data.  Only diagonal
                 elements are stored
    """
    cdef unsigned int num_elem = 2*generator.num_qubits
    cdef double[::1] m3_cals = np.zeros(num_elem, dtype=float)
    cdef unsigned int num_circuits = generator.length
    cdef unsigned int num_qubits = generator.num_qubits
    # Assuming each circuit is sampled the same
    cdef unsigned int shots_per_circuit = sum(counts[0].values())
    # Divide total shots by 2 since each error pathway gets only half of the total
    cdef unsigned int denom = num_circuits*shots_per_circuit / 2

    cdef size_t kk, idx
    cdef umap[string, unsigned int] counts_map
    cdef unsigned char[::1] cal_string
    cdef umap[string, unsigned int].iterator end
    cdef umap[string, unsigned int].iterator it
    cdef unsigned int val

    for idx, cal_string in enumerate(generator):
        counts_map = dict(counts[idx])
        end = counts_map.end()
        it = counts_map.begin()
        while it != end:
            key = dereference(it).first
            val = dereference(it).second
            for kk in range(num_qubits):
                if (key[num_qubits-kk-1]-48) == cal_string[num_qubits-kk-1]:
                    if cal_string[num_qubits-kk-1]:
                        m3_cals[2*kk+1] += val
                    else:
                        m3_cals[2*kk] += val
            postincrement(it)
         
    # Normalize to probabilities
    for kk in range(num_elem):
        m3_cals[kk] /= denom

    return np.asarray(m3_cals)
