.. _expvals:

############################
Obtaining expectation values
############################

Given a quasi- or standard probability distribution, it is possible to compute the
expectation value of diagonal operators directly from the distributions (or collections)
of distributions.  This can be done using string representation for standard diagonal
operators such as ``I``, ``Z``, ``0`` or ``1``, or via dictionaries for custom operators.


Let us first generate some quasi-distributions by mitigating 2- and 3-qubit GHZ circuits on
a noisy-simulator.

.. jupyter-execute::

    import numpy as np
    from qiskit import *
    from qiskit.providers.fake_provider import FakeAthens
    import mthree

    backend = FakeAthens()

    ghz2 = QuantumCircuit(2)
    ghz2.h(0)
    ghz2.cx(0,1)
    ghz2.measure_all()

    trans_ghz2 = transpile(ghz2, backend)

    ghz3 = QuantumCircuit(3)
    ghz3.h(0)
    ghz3.cx(0,1)
    ghz3.cx(1,2)
    ghz3.measure_all()

    trans_ghz3 = transpile(ghz3, backend)

    raw2 = backend.run(trans_ghz2, shots=4000).result().get_counts()
    raw3 = backend.run(trans_ghz3, shots=4000).result().get_counts()

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()

    quasi2 = mit.apply_correction(raw2, [0,1], return_mitigation_overhead=True)
    quasi3 = mit.apply_correction(raw3, [0,1,2], return_mitigation_overhead=True)


Now let us compute the expectaion values of these distributions for the default
case of ``Z`` operators on each qubit:

.. jupyter-execute::

    print('GHZ2:', quasi2.expval())
    print('GHZ3:', quasi3.expval())


The values are close to one and zero, respectively.  We can use strings to repeat the
above via:

.. jupyter-execute::

    print('GHZ2:', quasi2.expval('ZZ'))
    print('GHZ3:', quasi3.expval('ZZZ'))


Replacing a ``Z`` measurement with an ``I`` on one of the qubits has the affect of changing the
sign for the :math:`|1>^{\otimes N}` component:

.. jupyter-execute::

    print('GHZ2:', quasi2.expval('IZ'))
    print('GHZ3:', quasi3.expval('ZIZ'))

We can also pass lists of strings:

.. jupyter-execute::

    quasi3.expval_and_stddev(['ZZZ','ZIZ'])

Alternatively, users can specify their own custom diagonal operators using dictionaries.  Here
we form the projectors on the all ones and zeros states:

.. jupyter-execute::

    all_zeros_proj = {'000': 1}
    all_ones_proj = {'111': 1}
    quasi3.expval(all_zeros_proj)

Like strings, one can pass an array of dicts:

.. jupyter-execute::

    quasi3.expval([all_zeros_proj, all_ones_proj])


We can verify that the projectors return the correct values:

.. jupyter-execute::

    p0s, p1s = quasi3.expval([all_zeros_proj, all_ones_proj])
    np.allclose([p0s, p1s], [quasi3['000'], quasi3['111']])
