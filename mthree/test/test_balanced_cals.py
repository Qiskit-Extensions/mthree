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

"""Test balanced cals"""
from mthree.mitigation import _balanced_cal_strings


def test_balanced_strings():
    """Validate balanced cal string pairs sum to the num_qubits"""

    for num_qubits in [1, 2, 5, 9, 22, 47, 102]:
        cal_strs = _balanced_cal_strings(num_qubits)
        for kk in range(num_qubits):
            _sum = 0
            str1 = cal_strs[2*kk]
            str2 = cal_strs[2*kk+1]
            for jj in range(num_qubits):
                _sum += int(str1[jj]) + int(str2[jj])
            assert _sum == num_qubits
