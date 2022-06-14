# This code is part of Mthree.
#
# (C) Copyright IBM 2022.
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
from libcpp.string cimport string
from libcpp.unordered_map cimport unordered_map  as map

@cython.boundscheck(False)
def cy_marginal_counts(object counts, int[::1] indices):
    """Computes marginal counts from a given dictionary for the supplied indices.
    
    Parameters:
        counts (dict): Input counts dictionary with integer values.
        indices (ndarray): Int32 array of indices to keep.
        
    Returns:
        dict: Dictionary of marginal counts
    """
    cdef map[string, int] new_counts
    cdef map[string, int].iterator it
    cdef string key, new_key
    cdef int val
    cdef unsigned int key_len = len(next(iter(counts)))
    cdef size_t idx
    cdef unsigned int ind_len = indices.shape[0]

    new_key = '0'*ind_len
    for key, val in counts.items():
        for idx in range(ind_len):
            new_key[ind_len-idx-1] = key[key_len-indices[idx]-1]
        
        it = new_counts.find(new_key)
        if it == new_counts.end():
            new_counts[new_key] = val
        else:
            new_counts[new_key] += val
    return new_counts


@cython.boundscheck(False)
def cy_marginal_distribution(object counts, int[::1] indices):
    """Computes marginal distribution from a given dictionary for the supplied indices.
    
    Parameters:
        counts (dict): Input counts dictionary with double values.
        indices (ndarray): Int32 array of indices to keep.
        
    Returns:
        dict: Dictionary of marginal counts
    """
    cdef map[string, double] new_counts
    cdef map[string, double].iterator it
    cdef string key, new_key
    cdef double val
    cdef unsigned int key_len = len(next(iter(counts)))
    cdef size_t idx
    cdef unsigned int ind_len = indices.shape[0]

    new_key = '0'*ind_len
    for key, val in counts.items():
        for idx in range(ind_len):
            new_key[ind_len-idx-1] = key[key_len-indices[idx]-1]
        
        it = new_counts.find(new_key)
        if it == new_counts.end():
            new_counts[new_key] = val
        else:
            new_counts[new_key] += val
    return new_counts
