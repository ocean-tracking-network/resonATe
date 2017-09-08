
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

    from resonate.uniqueid import add_unqdetecid
    
    input_file = '/path/to/detections.csv'
    
    unqdet_det = add_unqdetecid(input_file);

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    unqdet_det.to_csv('/path/to/output.csv', index=False)
