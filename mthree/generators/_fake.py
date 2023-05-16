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

"""Fake bit-array generator"""
import numpy as np

from mthree.exceptions import M3Error


class FakeGenerator:
    """Fake generator"""

    def __init__(self, strings):
        """A fake generator instance used for testing.

        Parameters:
            strings (list):  List of np.uint8 dtype arrays

        Raises:
            M3Error: Array dtype is not np.uint8
        """
        self.strings = strings
        self.length = len(strings)
        self._iter_index = 0

        for string in self.strings:
            if string.dtype != np.uint8:
                raise M3Error("Dtype is not np.uint8")

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < self.length:
            self._iter_index += 1
            return self.strings[self._iter_index - 1]
        else:
            raise StopIteration
