
Cohort
======

.. raw:: html

   <hr>

The tool takes a dataframe of compressed detections and a time parameter
in minutes. It identifies groups of animals traveling together. Each
station an animal visits is checked for other animals detected there
within the specified time period.

The function returns a dataframe which you can use to help identify
animal cohorts. The cohort is created from the compressed data that is a
result from the ``compress_detections()`` function. Pass the compressed
dataframe into the ``cohort()`` function along with a time interval in
minutes (default is 60) to create the cohort dataframe.

.. code:: python

    from otntoolbox.cohorts import cohort
    from otntoolbox.compress import compress_detections
    import pandas as pd
    
    time_interval = 60
    
    data = pd.read_csv('../tests/assertion_files/nsbs.csv')
    
    compressed_df = compress_detections(data)
    
    cohort_df = cohort(compressed_df, time_interval)
    
    cohort_df

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    # Saves the cohort file
    cohort_df.to_csv('/path/to/output.csv', index=False)
