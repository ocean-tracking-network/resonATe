
# Detections Compression
------------------------

Compresses your detection files. Compressed detection files are needed
for the tools, such as interval and cohort. Important: Input files must
include the following manadatory columns: dataecollected, catalognumber
and unqdetecid.

.. code:: ipython2

    #%cd /home/user/data/ # uncomment to change the working directory
    from otntoolbox.compress import compress_detections
    import pandas as pd
    
    # Input detection file (uncompressed) file -> pandas DataFrame object
    detections = pd.read_csv('/Users/alexnunes/Desktop/otn-toolbox/tests/assertion_files/nsbs.csv')
    
    # Runs the compression operation and exports the compressed detection file
    compressed = compress_detections(detections=detections)
    compressed # preview compression

.. code:: ipython2

    # Save your compressed detection DataFrame to a CSV 
    compressed.to_csv('', index=False)
