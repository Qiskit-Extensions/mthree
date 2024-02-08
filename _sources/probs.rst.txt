.. _probs:

##########################
Converting to probabilites
##########################

M3 natively works with quasi-probability distributions; distributions that contain negative values
but nonetheless sum to one.  This is useful for mitigating expectation values, but there could
be situations where a true probability distribution is useful / needed.  To this end, it is
possible to find the closest probability distribution to a quasi-probability distribution in
terms of :math:`L2`-norm using:
:meth:`mthree.classes.QuasiDistribution.nearest_probability_distribution`.  This conversion is
done in linear time.

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

    trans_qc = transpile(qc, backend)
    raw_counts = backend.run(trans_qc, shots=8192).result().get_counts()

    quasis = mit.apply_correction(raw_counts, range(6))

    # Here is where the conversion happens
    quasis.nearest_probability_distribution()
