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
# cython: c_string_type=unicode, c_string_encoding=UTF-8
cimport cython
import numpy as np
cimport numpy as np
from libcpp.map cimport map
from libcpp.string cimport string
from cython.operator cimport dereference, postincrement

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void counts_to_internal(map[string, float] * counts_map,
                             unsigned char * vec,
                             float * probs,
                             unsigned int num_bits,
                             float shots):
    """Converts a Qiskit counts object (or Python dict) into an array
    of bitstrings and probabilities.
    
    Parameters:
        counts (object): A Qiskit counts object or Python dict.
        vec (unsigned char *): Pointer to array of bitstrings to populate.
        probs (float *): Pointer to array of probabilities to populate.
        num_bits (unsigned int): Number of bits in the bitstrings.
    """
    cdef unsigned int idx, letter, start
    cdef map[string, float].iterator end = counts_map.end()
    cdef map[string, float].iterator it = counts_map.begin()
    cdef string temp
    idx = 0
    while it != end:
        start = num_bits*idx
        probs[idx] = dereference(it).second / shots
        temp = dereference(it).first
        for letter in range(num_bits):
            vec[start+letter] = <unsigned char>temp[letter]-48
        idx += 1
        postincrement(it)


@cython.boundscheck(False)
@cython.cdivision(True)
cdef void internal_to_probs(map[string, float] * counts_map,
                            float * probs):
    """Converts internal arrays back into a Python dict.
    
    Parameters:
        vec (unsigned char *): Pointer to array of bitstrings.
        vec (float *): Pointer to array of probabilities.
        num_elems (unsigned int): Number of elements.
        num_bits (unsigned int): Number of bits in the bitstrings.
    """
    cdef size_t idx = 0
    cdef map[string, float].iterator end = counts_map.end()
    cdef map[string, float].iterator it = counts_map.begin()

    while it != end:
        dereference(it).second = probs[idx]
        idx += 1
        postincrement(it)


def counts_to_bitstrings_and_probs(object counts):
    """Convert counts to NumPy arrays of bitstrings and probabilities

    Parameters:
        counts (object): Dict or Counts object of counts data

    Returns:
        ndarray: Array of unsigned char bitstrings
        ndarray: Array of float probabilities
    """
    cdef float shots = sum(counts.values())
    cdef map[string, float] counts_map = counts
    cdef unsigned int num_elems = counts_map.size()
    cdef unsigned int num_bits = len(next(iter(counts)))

    cdef unsigned char[::1] bitstrings = np.empty(num_bits*num_elems, dtype=np.uint8)
    cdef float[::1] probs = np.empty(num_elems, dtype=np.float32)

    _core_counts_to_bp(&counts_map, num_bits, shots,
                       &bitstrings[0], &probs[0])

    return np.asarray(bitstrings), np.asarray(probs)


@cython.cdivision(True)
cdef void _core_counts_to_bp(map[string, float] * counts_map,
                             unsigned int num_bits,
                             float shots,
                             unsigned char * bitstrings,
                             float * probs):

    cdef unsigned int idx, letter, start
    cdef map[string, float].iterator end = counts_map.end()
    cdef map[string, float].iterator it = counts_map.begin()
    cdef string temp
    idx = 0
    while it != end:
        start = num_bits*idx
        probs[idx] = dereference(it).second / shots
        temp = dereference(it).first
        for letter in range(num_bits):
            bitstrings[start+letter] = <unsigned char>temp[letter]-48
        idx += 1
        postincrement(it)
