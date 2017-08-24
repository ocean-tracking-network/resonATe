
Unique Detections ID
====================

.. raw:: html

   <hr>

Adds the **uniquecid** column to your input file. The uniquecid column
assigns every detection record a unique numerical value. This column is
needed in order to perform operations, such as filter and compression
functions.

.. code:: python

    #%cd /home/user/data/ # uncomment to change the working directory
    from otntoolbox.uniqueid import add_unqdetecid
    
    # CSV file without unqdetecid column
    input_file = ''
    
    # Creates a new file including the uniqdecid column
    unqdet_det = add_unqdetecid(input_file);

.. code:: python

    # Modify and run this cell to save the changes to an output CSV file
    output_path = ''
    unqdet_det.to_csv(output_path, index=False)
