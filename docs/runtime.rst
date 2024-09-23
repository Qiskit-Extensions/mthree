.. _runtime:

########################
Using Runtime containers
########################

The Qiskit Runtime has two execution containers, `Batch` and `Session`, that allow for grouping
multiple jobs.  You can include M3 calibration jobs in these containers using the `mode` argument 
in `mthree.M3Mitigation.cals_from_system`.  For example:

.. jupyter-execute::

    from qiskit_ibm_runtime import Batch
    from qiskit_ibm_runtime.fake_provider import FakeCasablancaV2
    import mthree

    backend = FakeCasablancaV2()
    batch = Batch(backend=backend)

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(mode=batch); # This is where the Batch or Session goes

