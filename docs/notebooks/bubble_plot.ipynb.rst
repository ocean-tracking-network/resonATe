Bubble Plot
===========

The bubble plot function returns a Plotly scatter plot layered ontop of
a map. The color of the markers will indicate the number of detections
at each location. Alternatively, you can indicate the number of
individuals seen at each location by using ``type = 'individual'``.

.. warning:: 

   Input files must include ``station`` , ``catalognumber``, ``unqdetecid``, ``latitude``, ``longitude``, and ``datecollected`` as  columns.

.. code:: python

    from resonate.bubble_plot import bubble_plot
    import pandas as pd
    import plotly.offline as py
    
    df = pd.read_csv('/path/to/detections.csv')

To display the plot in iPython use:

.. code:: python

    bubble_plot(df)

Or use the standard plotting function to save as HTML:

.. code:: python

    bubble_plot(df,ipython_display=False, filename='/path_to_plot.html')

You can also do your count by number of individuals by using
``type = 'individual``:

.. code:: python

    bubble_plot(df, type='individual')

.. raw:: html

   <hr/>

Mapbox
------

Alternatively you can use a Mapbox access token plot your map. Mapbox is
much for responsive than standard Scattergeo plot.

Example Code
~~~~~~~~~~~~

.. code:: python

    mapbox_access_token = 'ADD_YOUR_TOKEN_HERE'
    bubble_plot(df, mapbox_token=mapbox_access_token)
