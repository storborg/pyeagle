Quick Start
===========


Install
-------

Install with pip::

    $ pip install pyeagle


Use
---

Open a library file, print some info about the contents.

.. code-block:: python

    import pyeagle

    lib = pyeagle.open('SparkFun-Sensors.lbr')

    for device_set in lib:  # could also use lib.device_sets
        print device_set

    for symbol in lib.symbols:
        print symbol

    for package in lib.packages:
        print package
