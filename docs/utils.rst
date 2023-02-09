.. _utils:

#################
Utility functions
#################

There are a couple of functionalities that are needed for easy mitigation, but are not part of the
Qiskit SDK and thus are included in M3.  Each is detailed below.

Final-measurement mapping
=========================

We have already seen the :func:`mthree.utils.final_measurement_mapping` routine in the section
on detailing with :ref:`Transpiled circuits<transpiled>`, where the addition of SWAP gates
made it difficult to determine exactly which physical qubits are being used, and which classical
bits they correspond to.  Here we show another example of this usage.  First we start with a 
7-qubit GHZ state:

.. jupyter-execute::

    from qiskit import *
    from qiskit.providers.fake_provider import FakeCasablanca
    import mthree

    qc = QuantumCircuit(7)
    qc.h(0)
    qc.cx(0, range(1,7))
    qc.measure_all()
    qc.draw('mpl')

and then transpile it:

.. jupyter-execute::

    backend = FakeCasablanca()
    trans_qc = transpile(qc, backend, optimization_level=3, seed_transpiler=54321)
    trans_qc.draw('mpl')

Once again we see that the physical qubits used and to which classical bits they map
to is non-trivial to find.  Yet this information is critical for successfully mitigating
the results.  This is where the :func:`mthree.utils.final_measurement_mapping` plays
a critical role:

.. jupyter-execute::

    mapping = mthree.utils.final_measurement_mapping(trans_qc)
    mapping

The keys of this mapping index the classical bits, whereas the
values tell you which qubits were measured to obtain the bit values.
The mapping is ordered in terms of the classical bit indices.  You can just pass the
generated ``mapping`` into M3 functions.


Evaluating raw counts data
==========================

When mitigating results one often wants to know how much better the results are with
mitigation compared to without.  However, Qiskit does not have great support for
computing things like expectation values.  So M3 includes the generic functions
:func:`mthree.utils.expval`, :func:`mthree.utils.stddev`, and
:func:`mthree.utils.expval_and_stddev` that operate on the native
``Counts`` objects in Qiskit.

For example let us compare raw data verse the mitigated results in a simple case.

.. jupyter-execute::

    from qiskit.providers.fake_provider import FakeAthens
    backend = FakeAthens()
    qc = QuantumCircuit(4)
    qc.h(2)
    qc.cx(2, 1)
    qc.cx(2, 3)
    qc.cx(1, 0)
    qc.measure_all()

    raw_counts = execute(qc, backend).result().get_counts()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    mit_counts = mit.apply_correction(raw_counts, qubits=range(4),
                                      return_mitigation_overhead=True)

    print('Raw counts expval', mthree.utils.expval(raw_counts))
    print('Mitigated expval', mit_counts.expval())


We can also compare things like upper-bounds on the standard deviation:

.. jupyter-execute::

    print('Raw counts uncertainty', mthree.utils.stddev(raw_counts))
    print('Mitigated uncertainty', mit_counts.stddev())

where the uncertainty for the raw ``Counts`` data is just :math:`1/\sqrt{\rm{shots}}`.

These convenence functions work in the same manner as the methods for the distribution
classes :class:`mthree.classes.QuasiDistribution` and :class:`mthree.classes.ProbDistribution`
and collections :class:`mthree.classes.QuasiCollection` and
:class:`mthree.classes.ProbCollection`.  That is to say that, for example,  I can pass operators to
``expval`` function:

.. jupyter-execute::

    print('These should be equal:', mthree.utils.expval(raw_counts, 'IIII'),
          mit_counts.expval('IIII'))

The routines also allow you to pass the native M3 distributions and collections. E.g.

.. jupyter-execute::

    print(mthree.utils.expval(mit_counts), mit_counts.expval())


Finally we note that you can pass multiple values at the same time.  Here we run and
mitigate 5 circuits:

.. jupyter-execute::

    raw_counts = execute([qc]*5, backend).result().get_counts()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system()
    mit_counts = mit.apply_correction(raw_counts, qubits=range(4),
                                      return_mitigation_overhead=True)


    print('Raw counts expval', mthree.utils.expval(raw_counts))
    print('Mitigated expval', mit_counts.expval())
