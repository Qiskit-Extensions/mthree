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

from mthree.exceptions import M3Error


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


class RandomComplimentGenerator:
    """Random compliment bit-array generator"""
    def __init__(self, num_qubits, num_arrays=16, seed=None):
        """Generator of compliment random arrays corresponding to 
        random x-gates on qubits for TexMex mitigation

        Parameters:
            num_qubits (int): Number of qubits
            num_arrays (int): Number of arrays to generate, default=16
            seed (int): seed for RNG, default=None

        Attributes:
            num_qubits (int): Number of qubits / length of arrays
            length (int): Total number of generated arrays, default=16
            seed (int): Seed used for RNG

        Raises:
            M3Error: Number of requested arrays is not even
        """
        self.seed = seed
        if self.seed is None:
            self.seed = np.random.randint(0, np.iinfo(np.int32).max)
        self._RNG = np.random.default_rng(seed=self.seed)
        self.num_qubits = num_qubits
        if num_arrays % 2:
            raise M3Error('num_arrays must be even')
        self.length = num_arrays
        self._iter_index = 0
        self._previous_array = None

    def __iter__(self):
        self._RNG = np.random.default_rng(seed=self.seed)
        self._iter_index = 0
        self._previous_array = None
        return self

    def __next__(self):
        if self._iter_index < self.length:
            self._iter_index += 1
            if self._iter_index % 2:
                out = self._RNG.integers(0, 2, size=self.num_qubits, dtype=np.uint8)
                self._previous_array = out
                return out
            else:
                return (self._previous_array + 1) % 2
        else:
            raise StopIteration
