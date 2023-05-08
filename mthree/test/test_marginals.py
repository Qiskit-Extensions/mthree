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
# pylint: disable=no-name-in-module

"""Test marginals"""
import mthree


def test_marginals1():
    """Test marginal indices return expected values"""
    counts = {
        "011": 123,
        "111": 4554,
        "101": 180,
        "100": 21,
        "001": 72,
        "110": 114,
        "010": 30,
        "000": 4906,
    }

    marginal_zero = mthree.utils.marginal_distribution(counts, [0])
    assert marginal_zero["0"] == 5071
    assert marginal_zero["1"] == 4929

    marginal_zero_two = mthree.utils.marginal_distribution(counts, [0, 2])
    assert marginal_zero_two["00"] == 4936
    assert marginal_zero_two["10"] == 135
    assert marginal_zero_two["01"] == 195
    assert marginal_zero_two["11"] == 4734

    marginal_two_zero = mthree.utils.marginal_distribution(counts, [2, 0])
    assert marginal_two_zero["00"] == marginal_zero_two["00"]
    assert marginal_two_zero["10"] == marginal_zero_two["01"]
    assert marginal_two_zero["01"] == marginal_zero_two["10"]
    assert marginal_two_zero["11"] == marginal_zero_two["11"]


def test_marginals2():
    """Test marginals using operators works as expected"""
    counts = {
        "011": 123,
        "111": 4554,
        "101": 180,
        "100": 21,
        "001": 72,
        "110": 114,
        "010": 30,
        "000": 4906,
    }

    marginal_zero = mthree.utils.marginal_distribution(counts, "IIZ")
    assert marginal_zero["0"] == 5071
    assert marginal_zero["1"] == 4929

    marginal_zero_two = mthree.utils.marginal_distribution(counts, "ZIZ")
    assert marginal_zero_two["00"] == 4936
    assert marginal_zero_two["10"] == 135
    assert marginal_zero_two["01"] == 195
    assert marginal_zero_two["11"] == 4734

    # Note that operators only have right to left ordering of the indices
    # So having marginal_two_zero tests here makes no sense


def test_marginals3():
    """Test marginals return the correct mappings"""
    counts = {
        "011": 123,
        "111": 4554,
        "101": 180,
        "100": 21,
        "001": 72,
        "110": 114,
        "010": 30,
        "000": 4906,
    }

    list_mapping = [12, 15, 18]
    dict_mapping = {0: 12, 1: 15, 2: 18}

    _, out_list_map = mthree.utils.marginal_distribution(
        counts, "IIZ", mapping=list_mapping
    )
    assert out_list_map == [12]

    _, out_dict_map = mthree.utils.marginal_distribution(
        counts, "IIZ", mapping=dict_mapping
    )
    assert out_dict_map == {0: 12}

    _, out_list_map = mthree.utils.marginal_distribution(
        counts, "ZIZ", mapping=list_mapping
    )
    assert out_list_map == [12, 18]

    _, out_dict_map = mthree.utils.marginal_distribution(
        counts, "ZIZ", mapping=dict_mapping
    )
    assert out_dict_map == {0: 12, 1: 18}

    _, out_list_map = mthree.utils.marginal_distribution(
        counts, [2, 0], mapping=list_mapping
    )
    assert out_list_map == [18, 12]

    _, out_dict_map = mthree.utils.marginal_distribution(
        counts, [2, 0], mapping=dict_mapping
    )
    assert out_dict_map == {0: 18, 1: 12}
