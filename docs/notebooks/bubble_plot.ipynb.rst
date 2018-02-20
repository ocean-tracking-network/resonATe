
Bubble Plot
===========

The bubble plot function returns a Plotly scatter plot layered ontop of
a map. The color of the markers will indicate the number of detections
at each location. Alternatively, you can indicate the number of
individuals seen at each location by using ``type = 'individual``.

.. warning:: 

    Input files must include ``station`` , ``catalognumber``, ``unqdetecid``, ``latitude``, ``longitude``, and ``datecollected`` as  columns.

.. code:: ipython3

    from resonate.bubble_plot import bubble_plot
    import pandas as pd
    import plotly.offline as py
    
    df = pd.read_csv('../tests/assertion_files/nsbs.csv')

To display the plot in iPython use:

.. code:: ipython3

    bubble_plot(df)

Or use the standard plotting function to save as HTML:

.. code:: ipython3

    bubble_plot(df,ipython_display=False, filename='../docs/_static/bubble_plot.html')

You can also do your count by number of individuals by using
``type = 'individual``:

.. code:: ipython3

    bubble_plot(df, type='individual')
