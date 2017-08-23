
# Create cohorts file
---------------------

Creates a file which you can use to help identify animal cohorts.

.. code:: ipython2

    #%cd /home/user/data/ # uncomment to change the working directory
    from otntoolbox.cohorts import cohort
    from otntoolbox.compress import compress_detections
    import pandas as pd
    
    # Set your time interval here (in minutes).
    time_interval = 60
    
    # Supply a compressed detection file 
    # compressed_df = pd.read_csv('\path\to\compressed_detections.csv')
    
    # OR
    
    # Supply an uncompressed detection file
    compressed_df = compress_detections(pd.read_csv(''))
    
    
    # Create cohort file
    cohort_df = cohort(compressed_df, time_interval)
    
    # Preview cohort Data
    cohort_df

.. code:: ipython2

    # Saves the cohort file
    cohort_df.to_csv('', index=False)
