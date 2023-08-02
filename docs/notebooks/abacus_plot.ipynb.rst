Abacus Plot
===========

The abacus plot is a way to plot annimal along time. The function uses
Plotly to place your points on a scatter plot. ``ycolumn`` is used as
the y axis and ``datecollected`` is used as the x axis. ``color_column``
is used to group detections together and assign them a color.

.. warning:: 

   Input files must include ``datecollected`` as a column.

.. code:: python

    from resonate.abacus_plot import abacus_plot
    import pandas as pd
    
    df = pd.read_csv('/path/to/detections.csv')

To display the plot in iPython use:

.. code:: python

    abacus_plot(df, ycolumn='catalognumber', color_column='receiver_group')

Or use the standard plotting function to save as HTML:

.. code:: python

    abacus_plot(df, ipython_display=False, filename='example.html')

