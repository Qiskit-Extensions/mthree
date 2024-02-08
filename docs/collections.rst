.. _collections:

##############################
Using distribution collections
##############################

When you mitigate over multiple circuits the return object is a :class:`mthree.classes.QuasiCollection`

.. jupyter-execute::

    from qiskit import *
    from qiskit_ibm_runtime.fake_provider import FakeCasablanca
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

    backend = FakeCasablanca()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(range(6))

    trans_qc = transpile([qc]*10, backend)
    raw_counts = backend.run(trans_qc, shots=4000).result().get_counts()

    quasis = mit.apply_correction(raw_counts, range(6), return_mitigation_overhead=True)
    type(quasis)

``QuasiCollection`` objects allow one to work with multiple distributions in the same manner as
a single one.  E.g. we can get the mitigation overhead of the whole collection

.. jupyter-execute::

    quasis.mitigation_overhead

or compute expectation values and standard deviations over the full set:

.. jupyter-execute::

    quasis.expval_and_stddev('IZIZIZ')

