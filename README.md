# mthree

[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://badge.fury.io/py/mthree.svg)](https://badge.fury.io/py/mthree)
[![pypi](https://img.shields.io/pypi/dm/mthree.svg)](https://pypi.org/project/mthree/)
![workflow](https://github.com/Qiskit-Partners/mthree/actions/workflows/python-package-conda.yml/badge.svg)

Matrix-free Measurement Mitigation (M3).

M3 is a measurement mitigation technique that solves for corrected measurement probabilities using a dimensionality reduction step followed by either direct LU factorization or a preconditioned iterative method that nominally converges in O(1) steps, and can be computed in parallel. For example, M3 can compute corrections on 42 qubit GHZ problems in under two seconds on a quad-core machine (depending on the number of unique bitstrings in the output).

## Documentation

[Online Documentation @ Qiskit.org](https://qiskit.org/ecosystem/mthree/)

## Installation

You can `pip` install M3 in using PyPi via:

```bash
pip install mthree
```

This will install an OpenMP optimized version on Linux, and serial versions for OSX and Windows.  Alternatively, one can install from source:

```bash
pip install .
```

To enable openmp one must have an openmp 4.0+ enabled compiler and install with:

```bash
MTHREE_OPENMP=1 pip install .
```

### OpenMP on OSX

On OSX one must install GCC using homebrew:

```bash
brew install gcc
```

Then installation with openmp can be accomplished using a call like:

```bash
MTHREE_OPENMP=1 CC=gcc-14 CXX=g++14 python setup.py install
```

Note that previously the instructions said to install LLVM and NOT GCC.  However,
in the latest version of OSX (Sequoia) LLVM based installations will build, but segfault
upon execution. GCC however works fine, thus the change above.


## Usage

### Basic usage

M3 is simple to use:

```python
import mthree
# Specify a mitigator object targeting a given backend
mit = mthree.M3Mitigation(backend)

# Compute the 1Q calibration matrices for the given qubits and given number of shots
# By default it is over all backend qubits at 10000 shots.
mit.cals_from_system(qubits, shots)

# Apply mitigation to a given dict of raw counts over the specified qubits
m3_quasi = mit.apply_correction(raw_counts, qubits)
```

Note that here `qubits` is a list of which qubits are measured to yield the bits in the output.
For example the list `[4,3,1,2,0]` indicates that a measurement on physical qubit 4 was written to
classical bit zero in the output bit-strings, physical qubit 3 maps to classical bit 1, etc.
The fact that the zeroth bit is right-most in the bitstring is handled internally.

### Error bounds

It is possible to compute error bounds in a similarly efficient manner.  This is not done
by default, but rather turned on using:

```python
m3_quasi = mit.apply_correction(raw_counts, qubits, return_mitigation_overhead=True)
```

Then the distribution itself can be called to return things like the expectation value and the
standard deviation:

```python
expval, stddev = quasi.expval_and_stddev()
```

### Closest probability distribution

The results of M3 mitigation are quasi-probabilities that nominally contain small negative values.
This is suitable for use in computing corrected expectation values or sampling problems
where one is interested in the highest probability bit-string.  However, if one needs
a true probability distribution then it is possible to convert from quasi-probabilites to
the closest true probability distribution in L2-norm using:

```python
closest_probs = m3_quasi.nearest_probability_distribution()
```

## License

[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
