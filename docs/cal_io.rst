.. _calio:

###################################
Saving and loading calibration data
###################################

It is possible to save calibration data and, optionally, re-load it at a later time.
Let us generate some calibration data and save it.

.. jupyter-execute::

    from qiskit.providers.fake_provider import FakeCasablanca
    import mthree

    backend = FakeCasablanca()

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system([1, 3, 5], cals_file='my_cals.json')
    mit.single_qubit_cals

or,

.. jupyter-execute::

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system([1, 3, 5])
    mit.cals_to_file('my_cals.json')

We can then load this data at a later point in time using:


.. jupyter-execute::

    import mthree

    mit2 = mthree.M3Mitigation()
    mit2.cals_from_file('my_cals.json')
    mit2.single_qubit_cals
    