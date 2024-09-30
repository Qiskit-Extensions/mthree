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
from cython.parallel cimport prange
import numpy as np
cimport numpy as np
np.import_array()

from libc.stdlib cimport malloc, free
from libcpp.map cimport map
from libcpp.string cimport string
from libcpp cimport bool

from .converters cimport counts_to_internal


cdef extern from "src/distance.h" nogil:
    unsigned int hamming_terms(unsigned int num_bits,
                               unsigned int distance,
                               unsigned int num_elems)

cdef extern from "src/elements.h" nogil:
    void column_elements(const unsigned char * bitstrings,
                         const float * cals_ptr,
                         unsigned int num_elems,
                         unsigned int num_bits,
                         unsigned int distance,
                         float * W_ptr,
                         float *  col_norms_ptr,
                         int num_terms,
                         bool MAX_DIST)


def bitstring_int(str string):
    return int(string, 2)

@cython.boundscheck(False)
@cython.cdivision(True)
def _reduced_cal_matrix(object counts, float[::1] cals,
                        unsigned int num_bits, unsigned int distance):
    
    cdef float shots = sum(counts.values())
    cdef map[string, float] counts_map = counts
    cdef unsigned int num_elems = counts_map.size()
    cdef unsigned int MAX_DIST
    cdef int num_terms = -1

    MAX_DIST = distance == num_bits
    if not MAX_DIST:
        num_terms = <int>hamming_terms(num_bits, distance, num_elems)

    cdef float[::1,:] W = np.zeros((num_elems, num_elems), order='F', dtype=np.float32)

    cdef float[::1] col_norms = np.zeros(num_elems, dtype=np.float32)

    cdef unsigned char * bitstrings = <unsigned char *>malloc(num_bits*num_elems*sizeof(unsigned char))
    cdef float * input_probs = <float *>malloc(num_elems*sizeof(float))
    counts_to_internal(&counts_map, bitstrings, input_probs, num_bits, shots)

    cdef size_t ii, jj
    cdef float col_norm, _temp
    cdef dict out_dict = counts_map

    column_elements(bitstrings,
                    &cals[0],
                    num_elems,
                    num_bits,
                    distance,
                    &W[0,0],
                    &col_norms[0],
                    num_terms,
                    MAX_DIST)

    free(bitstrings)
    free(input_probs)
    return np.asarray(W), out_dict, np.asarray(col_norms)
