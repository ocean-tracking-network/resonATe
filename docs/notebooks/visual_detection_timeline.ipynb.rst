
.. code:: ipython2

    # Enter a detection CSV file and title text for the visualization
    import otntoolbox.html_maps as hmaps
    
    # render_map takes a detection extract CSV file as a data source, 
    # as well as a string indicating what the title of the plot should be. 
    # The title string will also be the filename for the HTML output, located in data/html
    
    # You can supply a basemap argument to choose from a few alternate basemap tilesets:
    # Available basemaps are:
    # 
    # no basemap set, or basemap='dark_layer' - CartoDB/OpenStreetMap Dark
    # basemap='Esri_OceanBasemap' - coarse ocean bathymetry
    # basemap='CartoDB_Positron' - grayscale land/ocean 
    # basemap='Stamen_Toner' - Stamen Toner - high-contrast black and white - black ocean
    
    
    hmaps.render_map("/Users/alexnunes/Desktop/otn-toolbox/tests/assertion_files/nsbs.csv", "Nova Scotia Blue Sharks")

