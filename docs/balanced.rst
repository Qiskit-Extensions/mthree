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

    from qiskit.test.mock import FakeAthens
    import mthree

    mthree.circuits.balanced_cal_strings(5)


For every position in the bit-string you will see that a `0` or `1` appears `N` times.
If there is a `0`, then that circuit samples the :math:`|0\rangle` state for that qubit,
similarly for the `1` element.  So when we execute the `2N` balanced calibration circuits
using `shots` number of samples, then each error rate in the calibration data is actually
being sampled `N*shots` times.  Because the number of samples determines the precision of
the calibration data, knowing this is quite important.

 This information can be used in two ways.  First, if one wants very precise calibration data
 then we can take advantage of this factor of `N` enhancement and call the calibration step
 as is:

 .. jupyter-execute::

    backend = FakeAthens()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(shots=10000)

For this `5` qubit system this will results in error rates sampled `50000` times.
Alternatively, we can divide the number of shots by `N` (making sure to take into
account odd `N`) and come up with a calibration routine where the total number
of shots is indepdendent of `N`

.. jupyter-execute::

    backend = FakeAthens()
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(shots=(10000+1)//backend.configuration().num_qubits)

for a fixed desired precision.  Note that the "+1" in the above is there to
account for the possibility of an odd `N`.  This makes the calibration procedure
for larger numbers of qubits more efficient.
