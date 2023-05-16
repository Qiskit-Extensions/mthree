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
"""mthree Hadamard array generator"""
cimport cython

from libc.stdlib cimport malloc, free
from libc.math cimport log2, floor

import numpy as np
cimport numpy as np

from mthree.exceptions import M3Error


cdef class HadamardGenerator():
    """Hadamard calibration generator"""
    cdef public str name
    cdef unsigned int p
    cdef unsigned char * integer_bits
    cdef unsigned char * out_bits
    cdef public unsigned int num_qubits
    cdef public unsigned int length
    cdef unsigned int _iter_index
    
    @cython.boundscheck(False)
    def __cinit__(self, unsigned int num_qubits):
        """Hadamard calibration generator
        
        Generates a set of bit-arrays that evenly
        sample all independent and pair-wise correlated
        measurement errors.

        References:
            Bravyi et al, Phys. Rev. A 103, 042605 (2021)
        """
        self.name = 'hadamard'
        self.num_qubits = num_qubits
        self.p = <unsigned int>floor(log2(num_qubits)+1)
        self.length = <unsigned int>(2**self.p)
        self.integer_bits = <unsigned char *>malloc(self.p*sizeof(unsigned char))
        # output set of bitstrings
        self.out_bits = <unsigned char *>malloc(num_qubits*sizeof(unsigned char))
        self._iter_index = 0
        
    def __dealloc__(self):
        if self.integer_bits is not NULL:
            free(self.integer_bits)
        if self.out_bits is not NULL:
            free(self.out_bits)
            
    def __iter__(self):
        self._iter_index = 0
        return self
    
    def __next__(self):
        if self._iter_index < self.length:
            self._iter_index += 1
            return self._generate_array(self._iter_index-1)
        else:
            raise StopIteration
        
    @cython.boundscheck(False)
    def _generate_array(self, unsigned int index):
        if index > self.length-1:
            raise M3Error('Index must within generator length {}'.format(self.length))
        cdef size_t kk, jj
        cdef unsigned int tot
        cdef list out = []

        # Set the bitstrings for the integer_bits
        for kk in range(self.p):
            self.integer_bits[self.p-kk-1] = (index >> kk) & 1

        for kk in range(self.num_qubits):
            tot = 0
            for jj in range(self.p):
                tot += self.integer_bits[self.p-jj-1] and ((kk+1) >> jj) & 1
            self.out_bits[kk] = tot % 2
            
        # Need to return copy since the underlying memory will be reused
        # It turns out that it is faster to copy the NumPy array then it is
        # to copy the underlying MemoryView
        return np.asarray((<np.uint8_t[:self.num_qubits]> self.out_bits)).copy()
