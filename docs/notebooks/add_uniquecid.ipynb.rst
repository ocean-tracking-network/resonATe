
Unique Detections ID
====================

.. raw:: html

   <hr>

Adds the **uniquecid** column to your input file. The uniquecid column
assigns every detection record a unique numerical value. This column is
needed in order to perform operations, such as filter and compression
functions.

The code below will add a unique detection ID column and return the
Pandas dataframe.

.. code:: python

    from otntoolbox.uniqueid import add_unqdetecid
    
    # CSV file without unqdetecid column
    input_file = 'example.csv'
    
    # Creates a new file including the uniqdecid column
    unqdet_det = add_unqdetecid(input_file);

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    # Modify and run this cell to save the changes to an output CSV file
    output_path = '/path/to/output.csv'
    unqdet_det.to_csv(output_path, index=False)
