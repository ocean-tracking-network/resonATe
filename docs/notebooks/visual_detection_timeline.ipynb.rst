Visual Timeline
===============

.. raw:: html

   <hr/>

This tool takes a detections extract file and generates a Plotly
animated timeline, either in place in an iPython notebook or exported
out to an HTML file.

.. warning:: 

   Input files must include ``datecollected``, ``catalognumber``, ``station``, ``latitude``, and ``longitude`` as columns.

.. code:: python

    from resonate.visual_timeline import timeline
    import pandas as pd
    detections = pd.read_csv("/path/to/detection.csv")
    timeline(detections, "Timeline")

Exporting to an HTML File
-------------------------

You can export the map to an HTML file by setting ``ipython_display`` to
``False``.

.. code:: python

    from resonate.visual_timeline import timeline
    import pandas as pd
    detections = pd.read_csv("/path/to/detection.csv")
    timeline(detections, "Timeline", ipython_display=False)

Mapbox
------

Alternatively you can use a Mapbox access token plot your map. Mapbox is
much for responsive than standard Scattergeo plot.

.. code:: python

    from resonate.visual_timeline import timeline
    import pandas as pd
    
    mapbox_access_token = 'YOUR MAPBOX ACCESS TOKEN HERE'
    detections = pd.read_csv("/path/to/detection.csv")
    timeline(detections, "Title", mapbox_token=mapbox_access_token)
