
Visual Timeline
===============

.. raw:: html

   <hr/>

``render_map()`` takes a detection extract CSV file as a data source, as
well as a string indicating what the title of the plot should be. The
title string will also be the filename for the HTML output, located in
an html file.

You can supply a basemap argument to choose from a few alternate basemap
tilesets. Available basemaps are:

-  No basemap set or ``basemap='dark_layer'`` - CartoDB/OpenStreetMap
   Dark
-  ``basemap='Esri_OceanBasemap'`` - coarse ocean bathymetry
-  ``basemap='CartoDB_Positron'`` - grayscale land/ocean
-  ``basemap='Stamen_Toner'`` - Stamen Toner - high-contrast black and
   white - black ocean

.. code:: python

    import resonate.html_maps as hmaps
    hmaps.render_map("/path/to/detection.csv", "Title")

