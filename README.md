# mthree

Matrix-free Measurement Mitigation (M3).

M3 is a measurement mitigation technique that solves for corrected counts using a dimensionality reduction step followed by either direct LU factorization or a precopnditioned iterative method that nominally converges in O(1) steps, and can be computed in parallel.  For example, M3 can compute corrections on 42 qubit GHZ problems in under two seconds on a quad-core machine (depending on the number of unique bitstrings in the output).

## Installation

Currently M3 needs to be installed from source:

```bash
python setup.py install
```

To enable openmp one must have an openmp enabled compiler and install with:

```bash
python setup.py install --with-openmp
```

Optionally one can also set `-march=native` using:

```bash
python setup.py install --with-native
```

The `openmp` and `native` flags can be used simultaneously using a comma.

### OpenMP on OSX

On OSX one must install LLVM using homebrew (You cannot use GCC):

```bash
brew install llvm
```

after which the following (or the like) must be executed in the terminal:

```bash
export PATH="/usr/local/opt/llvm/bin:$PATH"
```

and

```bash
export LDFLAGS="-L/usr/local/opt/llvm/lib -Wl,-rpath,/usr/local/opt/llvm/lib"
export CPPFLAGS="-I/usr/local/opt/llvm/include"
```

Then installation with openmp can be accomplished using:

```bash
CC=clang CXX=clang python setup.py install --with-openmp
```

## Usage

M3 is simple to use:

```python
import mthree
# Specify a mitigator object targeting a given backend
mit = mthree.M3Mitigation(backend)

# Compute the 1Q calibration matrices for the given qubits and given number of shots
# By default it is over all backend qubits at 8192 shots.
mit.cals_from_system(qubits, shots)

# Apply mitigation to a given dict of raw counts over the specified qubits
m3_quasi = mit.apply_correction(raw_counts, qubits)
```
Note that here `qubits` is a list of which qubits are measured to yield the bits in the output.
For example the list `[4,3,1,2,0]` indicates that a measurement on physical qubit 4 was written to
classical bit zero in the output bit-strings, physical qubit 3 maps to classical bit 1, etc.
The fact that the zeroth bit is right-most in the bitstring is handled internally.

The results of M3 mitigation are quasi-probabilities that contain small negative values.
This is suitable for use in computing corrected expectation values.  However, if one needs
a true probability distribution then it is possible to convert from quasi-probabilites to
the closest true probability distribution in L2-norm using:

```python
closest_probs = m3_quasi.nearest_probability_distribution()
```

An additional benefit of the way M3 works is that it is possible to compute the effect of mitigation when only
looking at errors that are up to a given Hamming distance away.  This slightly increases the computational cost, but
allows for investigating if large weight errors have much impact on the output.  This can be controlled by the `distance` keyword argument in `apply_correction`:

```python
m3_quasi = mit.apply_correction(raw_counts, qubits, distance=DIST)
```
By default, M3 computes errors out to the full distance.

## License

Apache 2.
