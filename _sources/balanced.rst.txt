.. _balanced:

#####################
Balanced calibrations
#####################

The default calibration method for M3 is what is called "balanced" calibration.  We came up
with this method as an intermediary step between truly "independent" calibrations that run
two circuits for each qubit to get the error rates for :math:`|0\rangle` :math:`|1\rangle`,
and "marginal" calibrations that execute only two circuits :math:`|0\rangle^{\otimes N}`
and :math:`|1\rangle^{\otimes N}`.  These two methods are expensive, or can lead to inaccurate
results when state prep errors are present, respectively.

Balanced calibrations run :math:`2N` circuits for :math:`N` measured qubits, but the calibration
circuits are chosen in such a way as to sample each error rate :math:`N` times.  For example,
consider the balanced calibration circuits for 5 qubits:

.. jupyter-execute::

    from qiskit_ibm_runtime.fake_provider import FakeAthens
    import mthree

    mthree.circuits.balanced_cal_strings(5)


For every position in the bit-string you will see that a `0` or `1` appears `N` times.
If there is a `0`, then that circuit samples the :math:`|0\rangle` state for that qubit,
similarly for the `1` element.  So when we execute the `2N` balanced calibration circuits
using `shots` number of samples, then each error rate in the calibration data is actually
being sampled `N*shots` times.  Thus, when you pass the `shots` value to M3, in the balanced
calibration mode internally it divides by the number of measured qubits so that the precision
matches the precison of the other methods.  That is to say that the following:

 .. jupyter-execute::

    backend = FakeAthens()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(method='balanced')

Will sample each qubit error rate `10000` times regardless of which method is used.  Moreover,
this also yields a calibration process whose overhead is independent of the number of qubits
used.  Note that, when using a simulator or "fake" device, M3 defaults to `independent`
calibration mode for efficiency.  As such, to enable `balanced` calibration on a simulator
one must explicitly set the `method`` as done above.
