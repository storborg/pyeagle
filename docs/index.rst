PyEAGLE - Read / Write Cadsoft EAGLE Files
==========================================

`Scott Torborg <http://www.scotttorborg.com>`_

PyEAGLE is an interchange API to read and write Cadsoft EAGLE XML (v6 and
later) schematic, library, and PCB layout files.

Some long term goals are:

* Comprehensive and round-trip-capable interface between Pythonic data
  structures and EAGLE's XML format, eliminating the impedance mismatch
  involved in manipulating EAGLE files in Python scripts.
* Traversal and net analysis helpers, to serve as a foundation for higher-level
  tools.
* Rendering capability in SVG.
* Command-line tools, including basic ``grep`` and ``lint`` tools.

At this point it is fairly incomplete and not 'production useful'.


Example Usage
=============

.. code-block:: python

    lib = pyeagle.open('SparkFun-Sensors.lbr')
    for part in lib:
        print part


Screenshot
==========

Everyone loves screenshots.


.. raw:: html

    <svg width="186.0" height="183.0"><line x2="53.18" y1="123.03" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="110.33" x1="53.18"/><line x2="59.53" y1="116.68" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="116.68" x1="46.83"/><line x2="59.53" y1="65.88" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="65.88" x1="46.83"/><line x2="65.88" y1="142.08" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="130.142" x1="65.88"/><line x2="65.88" y1="52.164" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="40.48" x1="65.88"/><line x2="40.48" y1="91.28" style="stroke:rgb(165, 75, 75);stroke-width:4" y2="142.08" x1="142.08"/><line x2="40.48" y1="142.08" style="stroke:rgb(165, 75, 75);stroke-width:4" y2="40.48" x1="40.48"/><line x2="116.68" y1="40.48" style="stroke:rgb(165, 75, 75);stroke-width:4" y2="78.58" x1="40.48"/><line x2="142.08" y1="78.58" style="stroke:rgb(165, 75, 75);stroke-width:4" y2="91.28" x1="116.68"/><line x2="116.68" y1="78.58" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="65.88" x1="116.68"/><text y="157.32" x="116.68" style="fill:rgb(165, 165, 165); font-size:17.780000; font-family:Consolas;" transform="scale(1 1)">&gt;NAME</text><text y="49.37" x="116.68" style="fill:rgb(165, 165, 165); font-size:17.780000; font-family:Consolas;" transform="scale(1 1)">&gt;VALUE</text><line x2="40.48" y1="116.68" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="116.68" x1="15.08"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="15.08" r="5.08" cy="116.68"/><line x2="40.48" y1="65.88" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="65.88" x1="15.08"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="15.08" r="5.08" cy="65.88"/><line x2="142.08" y1="91.28" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="91.28" x1="167.48"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="167.48" r="5.08" cy="91.28"/><line x2="65.88" y1="15.08" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="40.48" x1="65.88"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="65.88" r="5.08" cy="15.08"/><line x2="65.88" y1="167.48" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="142.08" x1="65.88"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="65.88" r="5.08" cy="167.48"/><line x2="116.68" y1="40.48" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="65.88" x1="116.68"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="116.68" r="5.08" cy="40.48"/><line x2="91.28" y1="40.48" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="65.88" x1="91.28"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="91.28" r="5.08" cy="40.48"/><line x2="91.28" y1="142.08" style="stroke:rgb(165, 75, 75);stroke-width:1" y2="116.68" x1="91.28"/><circle style="stroke:rgb(75, 165, 75);stroke-width:1;fill:transparent;" cx="91.28" r="5.08" cy="142.08"/></svg>


Contents
========

.. toctree::
    :maxdepth: 2

    quickstart
    api
    contributing


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
