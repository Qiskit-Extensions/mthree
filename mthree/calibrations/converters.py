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
"""Raw calibration conversion tools"""


FLIP_DICT = {'0': '1', '1': '0'}


def flip_and_combine(counts, mapping, generator, cal_mapping):
    """Flip measurement results according to a set of mask strings from a generator.

    This is used to generate data for TEXMEX mitigation.

    Parameters:
        counts (list): List of dicts of counts
        generator (Generator): An M3 generator object
    """
    if len(counts) != generator.length:
        raise Exception('counts and generator lengths do not match')
    new_dict = {}
    total_shots = 0
    for idx, mask_str in enumerate(generator):
        cnts = counts[idx]
        total_shots += sum(cnts.values())
        for key, val in cnts.items():
            new_key = "".join(FLIP_DICT[bit] if mask_str[kk] == 1 else bit for kk, bit in enumerate(key))
            if new_key in new_dict:
                new_dict[new_key] += val
            else:
                new_dict[new_key] = val
    # Go to probabilities
    for key, val in new_dict.items():
        new_dict[key] = val / total_shots
    return new_dict
