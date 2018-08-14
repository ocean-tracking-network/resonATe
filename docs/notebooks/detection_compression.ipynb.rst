
Compressing Detections
======================

.. raw:: html

   <hr>

Compressing detections is done by looking at the detection times and
locations of an animal. Any detections that occur successively in time,
and the time between detections does not exceed the ``timefilter``, in
the same location are combined into a single detection with a start and
end time. The result is a compressed detections Pandas DataFrame.

Compression is the first step of the Mihoff Interval Data Tool.
Compressed detection DataFrames are needed for the tools, such as
interval and cohort.

.. warning:: 

    Input files must include ``datecollected``, ``catalognumber``, and ``unqdetecid`` as columns.

.. code:: python

    from resonate.compress import compress_detections
    import pandas as pd
    
    detections = pd.read_csv('/path/to/data.csv')
    
    compressed = compress_detections(detections=detections)

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    compressed.to_csv('/path/to/output.csv', index=False)
