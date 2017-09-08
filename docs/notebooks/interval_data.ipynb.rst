
Interval Data
=============

.. raw:: html

   <hr>

``interval_data()`` takes a compressed detections DataFrame, a distance
matrix, and a detection radiues DataFrame and creates an interval data
DataFrame.

Intervals are lengths of time in which a station detected an animal.
Many consecutive detections of an animal are replaced by one interval.

.. code:: python

    from otntoolbox.filter_detections import get_distance_matrix
    from otntoolbox.compress import compress_detections
    from otntoolbox.interval_data_tool import interval_data
    import pandas as pd
    import geopy
    
    input_file = pd.read_csv("../tests/assertion_files/nsbs.csv") 
    compressed = compress_detections(input_file) 
    matrix = get_distance_matrix(input_file)

Set the station radius for each station name.

.. code:: python

    detection_radius = 400
    
    station_det_radius = pd.DataFrame([(x, geopy.distance.Distance(detection_radius/1000.0)) 
                                       for x in matrix.columns.tolist()], columns=['station','radius'])
    
    station_det_radius.set_index('station', inplace=True)
    
    station_det_radius 

You can modify individual stations if needed by using
``DatraFrame.set_value()`` from Pandas.

.. code:: python

    station_name = 'station'
    
    station_detection_radius = 500
    
    station_det_radius.set_value(station_name, 'radius', geopy.distance.Distance( station_detection_radius/1000.0 ))

Create the interval data by passing the compressed detections, the
matrix, and the station radii.

.. code:: python

    interval = interval_data(compressed_df=compressed, dist_matrix_df=matrix, station_radius_df=station_det_radius)
    
    interval

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    interval.to_csv('/path/to/output.csv', index=False)
