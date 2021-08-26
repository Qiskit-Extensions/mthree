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
# cython: c_string_type=unicode, c_string_encoding=UTF-8
"""mthree expectation value"""
from mthree.exceptions import M3Error

cimport cython
from libc.math cimport sqrt
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector
from libcpp.string cimport string
cdef unordered_map[Py_UCS4, vector[int]] oper_map

oper_map['I'] = [1, 1]
oper_map['Z'] = [1, -1]

@cython.boundscheck(False)
def exp_val(object quasi, unicode exp_ops=''):
    """Computes expectation values in computational basis for a supplied
    list of operators (Default is all Z).

    Parameters:
        quasi (dict): Input quasi-probability distribution.
        exp_ops (str): String representation of qubit operators to compute.

    Returns:
        float: Expectation value.
    """
    cdef int bits_len = len(next(iter(quasi)))
    if exp_ops == '':
        exp_ops = 'Z'*bits_len
    else:
        exp_ops = exp_ops.upper()
        if len(exp_ops) != bits_len:
            raise M3Error('exp_ops length does not equal number of bits.')
    # Find normalization to probs
    cdef double exp_val = 0
    cdef unicode key
    cdef double val
    cdef int oper_prod = 1
    cdef size_t kk
    for key, val in quasi.items():
        oper_prod = 1
        for kk in range(bits_len):
            oper_prod *= oper_map[exp_ops[kk]][<int>key[bits_len-kk-1]-48]
        exp_val += val * oper_prod
    return exp_val

@cython.boundscheck(False)
def exp_val_and_stddev(object probs, unicode exp_ops=''):
    """Computes expectation value and standard deviation in computational basis
    for a given probability distribution (not quasi-probs).

    Parameters:
        probs (dict): Input probability distribution.
        exp_ops (str): String representation of qubit operators to compute.

    Returns:
        float: Expectation value.
        float: Standard deviation.
    """
    # Find normalization to probs
    cdef int bits_len = len(next(iter(probs)))
    if exp_ops == '':
        exp_ops = 'Z'*bits_len
    else:
        exp_ops = exp_ops.upper()
        if len(exp_ops) != bits_len:
            raise M3Error('exp_ops length does not equal number of bits')
    # Find normalization to probs
    cdef double exp_val = 0
    cdef unicode key
    cdef double val
    cdef int oper_prod = 1
    cdef double stddev, exp2 = 0
    cdef size_t kk
    for key, val in probs.items():
        oper_prod = 1
        for kk in range(bits_len):
            oper_prod *= oper_map[exp_ops[kk]][<int>key[bits_len-kk-1]-48]
        exp_val += val * oper_prod
        exp2 += val
    
    stddev = sqrt((exp2 - exp_val*exp_val) / probs.shots)
    
    return exp_val, stddev
