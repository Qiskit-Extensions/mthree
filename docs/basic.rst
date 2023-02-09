.. _basic:

###########
Basic usage
###########

Using M3 involves three steps (steps one and two can usually be done in reverse order if desired).

    1) Select a system and calibrate over the desired set of qubits.

    2) Run the circuit(s) of interest on the system.

    3) Apply the readout correction and post-process.


Simple example
--------------
Here we use a noisy simulator to perform the three steps above.  First we import the
needed modules, and construct a circuit of interest.

.. jupyter-execute::

    import numpy as np
    from qiskit import *
    from qiskit.providers.fake_provider import FakeCasablanca
    import mthree

    qc = QuantumCircuit(6)
    qc.reset(range(6))
    qc.h(3)
    qc.cx(3,1)
    qc.cx(3,5)
    qc.cx(1,0)
    qc.cx(5,4)
    qc.cx(1,2)
    qc.measure_all()
    qc.draw('mpl')

Next we calibrate an M3 mitigator instance over qubits 0 -> 6 (Step #1):

.. jupyter-execute::

    backend = FakeCasablanca()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(range(6))

Transpile and execute our circuit (Step #2):

.. jupyter-execute::

    trans_qc = transpile(qc, backend)
    raw_counts = backend.run(trans_qc).result().get_counts()

Finally, apply the correction and post-process (Step #3).  Here our post-processing is
simply computing the expectation value from the returned quasi-probabilities:

.. jupyter-execute::

    quasis = mit.apply_correction(raw_counts, range(6))
    print('Expectation value:',quasis.expval())


Specifying qubits to mitigate over
----------------------------------
The circuit above also fits on other systems without SWAP mapping
provided that we select the correct layout.

.. jupyter-execute::

    from qiskit.providers.fake_provider import FakeMontreal

    backend = FakeMontreal()
    mit2 = mthree.M3Mitigation(backend)

In our case, ``qubits = [10, 12, 15, 13, 11, 14]`` is an appropriate layout.  Importantly, the
zeroth entry of the list tells us what physical qubit is readout to generate bit 0 in the output
bit-strings.  We must pass this list to both the calibration and correction steps of M3.

.. jupyter-execute::

    qubits = [10, 12, 15, 13, 11, 14]
    mit2.cals_from_system(qubits)

    trans_qc = transpile(qc, backend, initial_layout=qubits)
    raw_counts2 = backend.run(trans_qc).result().get_counts()

    quasis2 = mit2.apply_correction(raw_counts2, qubits)
    print('Expectation value:',quasis2.expval())

