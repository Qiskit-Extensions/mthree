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

"""Complete bit-array generator"""
import numpy as np

from mthree.exceptions import M3Error


class CompleteGenerator:
    """Complete basis set bit-array generator"""

    def __init__(self, num_qubits):
        """Generator of arrays for full 2**N set of computational 
        basis states

        Parameters:
            num_qubits (int): Number of qubits

        Attributes:
            num_qubits (int): Number of qubits / length of arrays
            length (int): Total number of generated arrays, default=16
            seed (int): Seed used for RNG
        """
        self.name = "complete"
        self.num_qubits = int(num_qubits)
        self.length = 2**num_qubits
        self._iter_index = 0

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < self.length:
            self._iter_index += 1
            return np.array([(self._iter_index-1 >> kk) & 1 
                             for kk in range(self.num_qubits-1,-1,-1)], dtype=np.uint8)
        else:
            raise StopIteration
