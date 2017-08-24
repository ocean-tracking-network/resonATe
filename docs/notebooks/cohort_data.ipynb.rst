
Cohort
======

.. raw:: html

   <hr>

Creates a file which you can use to help identify animal cohorts.

.. code:: python

    from otntoolbox.cohorts import cohort
    from otntoolbox.compress import compress_detections
    import pandas as pd
    
    # Set your time interval here (in minutes).
    time_interval = 60
    
    # Supply a compressed detection file 
    # compressed_df = pd.read_csv('\path\to\compressed_detections.csv')
    #
    # OR
    #
    # Supply an uncompressed detection file
    compressed_df = compress_detections(pd.read_csv(''))
    
    # Create cohort file
    cohort_df = cohort(compressed_df, time_interval)
    
    # Preview cohort Data
    cohort_df

.. code:: python

    # Saves the cohort file
    cohort_df.to_csv('', index=False)
