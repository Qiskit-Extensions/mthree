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

@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.cdivision(True)
def calibration_to_texmex(list counts, object generator):
    """Convert raw calibration data into TEXMEX data

    Parameters:
        counts (list): List of Counts objects
        generator (Generator): A generator object for calibration strings

    Returns:
        dict: Merged TEXMEX calibration dict
    """
    cdef char[::1] mask_str
    cdef umap[string, unsigned int] counts_map 
    cdef umap[string, double] out_map
    cdef umap[string, unsigned int].iterator end
    cdef umap[string, unsigned int].iterator it

    cdef umap[string, double].iterator double_end
    cdef umap[string, double].iterator double_it

    cdef string old_key, new_key
    cdef unsigned int temp_val, total_counts = 0
    cdef size_t idx
    cdef pair[string, double] dict_pair
    cdef pair[umap[string, double].iterator, bool] insert_pair

    if len(counts) != generator.length:
        raise Exception(f"Counts length ({len(counts)}) does not equal generator length ({generator.length})")

    for idx, mask_str in enumerate(generator):
        counts_map = dict(counts[idx])
        end = counts_map.end()
        it = counts_map.begin()

        while it != end:
            old_key = dereference(it).first
            temp_val = dereference(it).second
            new_key.clear()
            for kk in range(old_key.size()):
                if mask_str[kk]:
                    if <bool>(old_key[kk]-48):
                        new_key.push_back(48)
                    else:
                        new_key.push_back(49)
                else:
                    new_key.push_back(old_key[kk])

            total_counts += temp_val
            dict_pair.first = new_key
            dict_pair.second = temp_val
            insert_pair = out_map.insert(dict_pair)
            # Key already in map
            if not insert_pair.second:
                out_map[new_key] += temp_val
            postincrement(it)

    # convert counts to probabilies
    double_end = out_map.end()
    double_it = out_map.begin()
    while double_it != double_end:
        old_key = dereference(double_it).first
        out_map[old_key] /= total_counts
        postincrement(double_it)

    return out_map
