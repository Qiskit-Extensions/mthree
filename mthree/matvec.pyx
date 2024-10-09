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
import logging
cimport cython
from cython.parallel cimport prange
import numpy as np
cimport numpy as np
np.import_array()

from libcpp cimport bool
from libcpp.map cimport map
from libcpp.string cimport string
from cython.operator cimport dereference, postincrement

from mthree.converters cimport _core_counts_to_bp


cdef extern from "src/distance.h" nogil:
    unsigned int hamming_terms(unsigned int num_bits,
                               unsigned int distance,
                               unsigned int num_elems)

cdef extern from "src/elements.h" nogil:
    float compute_element(unsigned int row,
                          unsigned int col,
                          const unsigned char * bitstrings,
                          const float * cals,
                          unsigned int num_bits)


cdef extern from "src/col_renorm.h" nogil:
    void compute_col_norms(float * col_norms,
                           const unsigned char * bitstrings,
                           const float * cals,
                           unsigned int num_bits,
                           unsigned int num_elems,
                           unsigned int distance)


cdef extern from "src/matvec.h" nogil:
    void matvec(const float * x,
                float * out,
                float * col_norms,
                const unsigned char * bitstrings,
                const float * cals,
                unsigned int num_bits,
                unsigned int num_elems,
                unsigned int distance,
                int num_terms,
                bool MAX_DIST)

    void rmatvec(const float * x,
                 float * out,
                 float * col_norms,
                 const unsigned char * bitstrings,
                 const float * cals,
                 unsigned int num_bits,
                 unsigned int num_elems,
                 unsigned int distance,
                 int num_terms,
                 bool MAX_DIST)

logger = logging.getLogger(__name__)

cdef class M3MatVec():
    cdef public unsigned char[::1] bitstrings
    cdef public float[::1] probs
    cdef float[::1] col_norms
    cdef bool MAX_DIST
    cdef unsigned int distance
    cdef public unsigned int num_elems
    cdef public unsigned int num_bits
    cdef float[::1] cals
    cdef public dict sorted_counts
    cdef int num_terms
    
    def __cinit__(self, object counts, float[::1] cals, int distance=-1):
        
        cdef float shots = sum(counts.values())
        cdef map[string, float] counts_map = counts
        self.num_elems = counts_map.size()
        self.num_bits = len(next(iter(counts)))
        self.cals = cals
        self.sorted_counts = counts_map
        self.num_terms = -1
        
        if distance == -1:
            distance = self.num_bits

        self.distance = distance
        self.MAX_DIST = self.distance == self.num_bits
        if not self.MAX_DIST:
            self.num_terms = <int>hamming_terms(self.num_bits, self.distance, self.num_elems)
        
        logger.info(f"Number of Hamming terms: {self.num_terms}")
        
        self.bitstrings = np.empty(self.num_bits*self.num_elems, np.uint8)
        self.probs = np.empty(self.num_elems, np.float32)
        self.col_norms = np.empty(self.num_elems, np.float32)

        _core_counts_to_bp(&counts_map, self.num_bits, shots,
                           &self.bitstrings[0], &self.probs[0])
        
        compute_col_norms(&self.col_norms[0], &self.bitstrings[0], &self.cals[0],
                          self.num_bits, self.num_elems, distance)

        
    @cython.boundscheck(False)
    def get_col_norms(self):
        """
        Get the internally used column norms.

        Returns:
            ndarray: Column norms.
        """
        cdef size_t kk
        cdef float[::1] out = np.empty(self.num_elems, dtype=np.float32)
        for kk in range(self.num_elems):
            out[kk] = self.col_norms[kk]
        return np.asarray(out, dtype=np.float32)

    @cython.boundscheck(False)
    @cython.cdivision(True)
    def get_diagonal(self):
        cdef size_t kk
        cdef float temp_elem
        cdef float[::1] out = np.empty(self.num_elems, dtype=np.float32)
        for kk in range(self.num_elems):
            temp_elem = compute_element(kk, kk,&self.bitstrings[0],
                                        &self.cals[0], self.num_bits)
            temp_elem /= self.col_norms[kk]
            out[kk] = temp_elem
        return np.asarray(out, dtype=np.float32)

    @cython.boundscheck(False)
    def matvec(self, const float[::1] x):
        cdef size_t row
        if x.shape[0] != self.num_elems:
            raise Exception('Incorrect length of input vector.')
        cdef float[::1] out = np.empty(self.num_elems, dtype=np.float32)
        matvec(&x[0],
               &out[0],
               &self.col_norms[0],
               &self.bitstrings[0],
               &self.cals[0],
               self.num_bits,
               self.num_elems,
               self.distance,
               self.num_terms,
               self.MAX_DIST)
        return np.asarray(out, dtype=np.float32)

    @cython.boundscheck(False)
    def rmatvec(self, const float[::1] x):
        cdef size_t col
        if x.shape[0] != self.num_elems:
            raise Exception('Incorrect length of input vector.')
        cdef float[::1] out = np.empty(self.num_elems, dtype=np.float32)
        rmatvec(&x[0],
                &out[0],
                &self.col_norms[0],
                &self.bitstrings[0],
                &self.cals[0],
                self.num_bits,
                self.num_elems,
                self.distance,
                self.num_terms,
                self.MAX_DIST)
        return np.asarray(out, dtype=np.float32)


@cython.boundscheck(False)
@cython.cdivision(True)
cdef void counts_to_bitstrings(map[string, float] * counts_map,
                               unsigned char * bitstrings,
                               unsigned int num_bits):
   
    cdef unsigned int idx, letter, start
    cdef map[string, float].iterator end = counts_map.end()
    cdef map[string, float].iterator it = counts_map.begin()
    cdef string temp
    idx = 0
    while it != end:
        start = num_bits*idx
        temp = dereference(it).first
        for letter in range(num_bits):
            bitstrings[start+letter] = <unsigned char>temp[letter]-48
        idx += 1
        postincrement(it)
