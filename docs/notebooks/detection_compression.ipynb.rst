
Detections Compression
======================

.. raw:: html

   <hr>

Compresses your detection files. Compressed detection files are needed
for the tools, such as interval and cohort.

.. warning::  Input files must include ``dataecollected``, ``catalognumber``
	and ``unqdetecid`` as columns.

.. code:: python

    from otntoolbox.compress import compress_detections
    import pandas as pd
    
    detections = pd.read_csv('/path/to/data.csv')
    
    compressed = compress_detections(detections=detections)

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    compressed.to_csv('/path/to/output.csv', index=False)
