.. _expvals:

############################
Obtaining expectation values
############################

Given a quasi- or standard probability distribution, it is possible to compute the
expectation value of diagonal operators directly from the distributions (or collections)
of distributions:

.. jupyter-execute::

    import numpy as np
    from qiskit import *
    from qiskit.circuit.library import TwoLocal
    from qiskit.test.mock.backends import FakeCasablanca
    import mthree

    # Measure YZ
    qc_yz = QuantumCircuit(2)
    qc_yz.sdg(1)
    qc_yz.h(1)

    # Measure XX
    qc_xx = QuantumCircuit(2)
    qc_xx.h(0)
    qc_xx.h(1)

    qc = TwoLocal(2, rotation_blocks='ry', entanglement_blocks='cx') 
    circs = [qc.compose(qc_yz), qc, qc, qc.compose(qc_xx)]

    params = np.array([1.22253725, 0.39053752, 0.21462153, 5.48308027,
                       2.06984514, 3.65227416, 4.01911194, 0.35749589])

    bound_circs = [circ.bind_parameters(params).measure_all(inplace=False) for circ in circs]

    backend = FakeCasablanca()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system([0,1])

    trans_qc = transpile(bound_circs, backend)
    raw_counts = backend.run(trans_qc, shots=4000).result().get_counts()

    quasis = mit.apply_correction(raw_counts, [0,1], return_mitigation_overhead=True)

    quasis.expval()

By default, the expectation value is with respect to the standard Z-operators.  However, it is
possible to pass other diagonal operators either as a string or a list.  If given a list, the
number of elements must match the number of raw counts (in this example 4):

.. jupyter-execute::

    quasis.expval(['ZZ', 'ZI', 'II', 'ZZ'])