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

    for device in lib:  # could also use lib.devices
        print device

    for symbol in lib.symbols:
        print symbol

    for package in lib.packages:
        print package
