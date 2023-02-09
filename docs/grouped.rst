.. _grouped:

#################
Grouped operators
#################

Often times when evaluating expectation values it is possible to group operators
together if the Pauli operators from which they are comprised commute with each other.  when
possible, this batching can greatly reduce the number of executions needed.  To see how to do
this consider the following simple example:

.. jupyter-execute::

    from qiskit import *
    from qiskit.providers.fake_provider import FakeAthens
    import mthree

    qc = QuantumCircuit(4)
    qc.h(0)
    qc.cx(0, range(1, 4))
    qc.measure_all()
    qc.draw('mpl')

Here we will generate and execute two circuits on the target system (fake system in this case),
and, because we have transpiled, find the final measurement mapping:

.. jupyter-execute::

    backend = FakeAthens()
    trans_circs = transpile([qc]*2, backend, optimization_level=3, approximation_degree=0)
    mappings = mthree.utils.final_measurement_mapping(trans_circs)  

Let us execute and get the resultant counts:

.. jupyter-execute::

    job = backend.run(trans_circs, shots=10000)
    counts = job.result().get_counts()

We can now mitigate as usual:

.. jupyter-execute::

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(mappings, shots=10000)
    quasis = mit.apply_correction(counts, mappings, return_mitigation_overhead=True)

Now that we have the final mitigated quasi-distributions we can compute expectation values.
For batched operators, the expectation values are grouped together based on which quasi-distribution
you want to evaluate them with:

.. jupyter-execute::

    quasis.expval([['IIII', 'ZZZZ', '0000', '1111'], ['IIII']])

The return list has the expectation values grouped into NumPy arrays.  A similar procedure works
for expectation values and standard deviations:

.. jupyter-execute::

    quasis.expval_and_stddev([['IIII', 'ZZZZ', '0000', '1111'], ['IIII']])

If you have a single expectation value string then you do not need to wrap it in a list:

.. jupyter-execute::

    quasis.expval([['IIII', 'ZZZZ', '0000', '1111'], 'IIII'])

Of course probability-distributions work the same way as quasi-distributions:

.. jupyter-execute::

    probs = quasis.nearest_probability_distribution()
    probs.expval([['IIII', 'ZZZZ', '0000', '1111'], ['IIII']])

.. jupyter-execute::

    probs.expval_and_stddev([['IIII', 'ZZZZ', '0000', '1111'], ['IIII']])
