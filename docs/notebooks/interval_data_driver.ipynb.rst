
# Create Interval Data
----------------------

Creates a compressed detections table and an interval data file.
Intervals are lengths of time in which a station detected an animal.
Many consecutive detections of an animal are replaced by one interval.

.. code:: ipython2

    #%cd /home/user/data/ # uncomment to change the working directory
    from otntoolbox.filter_detections import get_distance_matrix
    from otntoolbox.compress import compress_detections
    from otntoolbox.interval_data_tool import interval_data
    import pandas as pd
    import geopy

.. code:: ipython2

    # Input DataFrames
    
    input_file = pd.read_csv("/Path") 
    compressed = compress_detections(input_file) # compressed detections
    matrix = get_distance_matrix(input_file) # station distance matrix

.. code:: ipython2

    # Set your station radius values
    detection_radius = 100 # (in meters) applies same detection radius to all stations
    
    station_det_radius = pd.DataFrame([(x, geopy.distance.Distance(detection_radius/1000.0)) for x in matrix.columns.tolist()], columns=['station','radius'])
    station_det_radius.set_index('station', inplace=True)
    station_det_radius # preview radius values

.. code:: ipython2

    # Modify and run this cell to change individual station detection radiuses
    station_name = 'station'
    station_detection_radius = 500 # Value in meters
    
    station_det_radius.set_value(station_name, 'radius', geopy.distance.Distance( station_detection_radius/1000.0 ))

.. code:: ipython2

    interval = interval_data(compressed_df=compressed, dist_matrix_df=matrix, station_radius_df=station_det_radius)
    interval #preview interval data

.. code:: ipython2

    # Saves the interval data file
    interval.to_csv('/path/to/output.csv', index=False)
