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

"""Random bit-array generator"""
import numpy as np


class RandomGenerator:
    """Random bit-array generator"""
    def __init__(self, num_qubits, num_arrays=16, seed=None):
        """Generator of random arrays corresponding to random x-gates on
        qubits for TexMex mitigation

        Parameters:
            num_qubits (int): Number of qubits
            num_arrays (int): Number of arrays to generate, default=16
            seed (int): seed for RNG, default=None

        Attributes:
            num_qubits (int): Number of qubits / length of arrays
            length (int): Total number of generated arrays, default=16
            seed (int): Seed used for RNG
        """
        self.seed = seed
        if self.seed is None:
            self.seed = np.random.randint(0, np.iinfo(np.int32).max)
        self._RNG = np.random.default_rng(seed=self.seed)
        self.num_qubits = num_qubits
        self.length = num_arrays
        self._iter_index = 0

    def __iter__(self):
        self._RNG = np.random.default_rng(seed=self.seed)
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < self.length:
            self._iter_index += 1
            return self._RNG.integers(0, 2, size=self.num_qubits, dtype=np.uint8)
        else:
            raise StopIteration
