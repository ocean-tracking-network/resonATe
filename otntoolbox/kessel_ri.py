import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.cm as cm
from datetime import datetime
import compress as cp
import folium as fl
import math

matplotlib.style.use('ggplot')


def total_days_diff(detections):
    """
    total_days_diff
    Determines the total days difference.

    The difference is determined
    by the minimal startdate of every detection and the maximum enddate of
    every detection. Both are converted into a datetime then subtracted to
    get a timedelta. The timedelta is converted to seconds and divided by
    the number of seconds in a day (86400). The function returns a floating
    point number of days (i.e. 503.76834).

    @var Detections - Pandas DataFrame pulled from the compressed detections
    CSV
    """
    first = datetime.strptime(detections.startdate.min(), "%Y-%m-%d %H:%M:%S")
    last = datetime.strptime(detections.enddate.max(), "%Y-%m-%d %H:%M:%S")
    total = last - first
    total = total.total_seconds()/86400.0
    return total





def total_days_count(detections):
    '''
    total_days_count
    The function below takes a Pandas DataFrame and determines the number of days any
    detections were seen on the array.

    The function converst both the startdate and enddate columns into a date with no hours, minutes,
    or seconds. Next it creates a list of the unique days where a detection was seen. The size of the
    list is returned as the total number of days as an integer.

    *** NOTE ****
    Possible rounding error may occur as a detection on 2016-01-01 23:59:59 and a detection on
    2016-01-02 00:00:01 would be counted as days when it is really 2-3 seconds.


    @var Detections - Pandas DataFrame pulled from the compressed detections CSV
    '''
    detections['startdate'] = detections['startdate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",)).apply(datetime.date)
    detections['enddate'] = detections['enddate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",)).apply(datetime.date)
    detections = pd.unique(detections[['startdate', 'enddate']].values.ravel())
    return detections.size





def aggregate_total_with_overlap(detections):
    '''
    aggregate_total_with_overlap

    The function below aggregates timedelta of startdate and enddate of each detection into
    a final timedelta then returns a float of the number of days. If the startdate and enddate
    are the same, a timedelta of one second is assumed.

    @var Detections - Pandas DataFrame pulled from the compressed detections CSV
    '''
    total = pd.Timedelta(0)
    detections['startdate'] = detections['startdate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))
    detections['enddate'] = detections['enddate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))
    detections['timedelta'] = detections['enddate'] - detections['startdate']

    for index, row in detections.iterrows():
        if row['timedelta'] > pd.Timedelta(0):
            diff = row['timedelta']
        else:
            diff = pd.Timedelta('1 second')
        total += diff
    return total.total_seconds()/86400.0





def aggregate_total_no_overlap(detections):
    '''
    aggregate_total_no_overlap

    The function below aggregates timedelta of startdate and enddate, excluding overlap between
    detections. Any overlap between two detections is converted to a new detection using the earlier
    startdate and the latest enddate. If the startdate and enddate are the same, a timedelta of one
    second is assumed.

    @var Detections - Pandas DataFrame pulled from the compressed detections CSV
    '''
    total = pd.Timedelta(0)

    # sort and convert datetimes
    detections = detections.sort_values(by='startdate', ascending=False).reset_index(drop=True)
    detections['startdate'] = detections['startdate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))
    detections['enddate'] = detections['enddate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))

    # A stack is used as an easy way to organize and maintain the detections
    detection_stack = detections.T.to_dict().values()

    # Run the loop while the stack is not empty
    while len(detection_stack) > 0:

        current_time_block = detection_stack.pop()

        # Make sure the current element is not empty
        if current_time_block:

            # Pop the next item if the stack is not empty
            if len(detection_stack) > 0:
                next_time_block = detection_stack.pop()
            else:
                next_time_block = False

            # Check to see if we are down to the last item in the stack or there is no overlap
            if not next_time_block or next_time_block['startdate'] > current_time_block['enddate']:

                # Create the timedelta and add it to the total, assuming 1 second if the timedelta equals 0
                diff = pd.Timedelta(0)
                diff += current_time_block['enddate'] - current_time_block['startdate']
                if diff == pd.Timedelta(0):
                    diff = pd.Timedelta('1 second')
                total += diff

                # Add the next block back into the stack so that it can be used in the next iteration
                detection_stack.append(next_time_block)
            else:

                # If there is overlap take a new endate, eliminating the overlap, and add it back into the stack for the next iteration
                current_time_block['enddate'] = max([current_time_block['enddate'], next_time_block['enddate']])
                detection_stack.append(current_time_block)

    # Return the value as a float in days
    return total.total_seconds()/86400.0





def get_days(dets, calculation_method='kessel'):
    '''
    get_days

    Determines which calculation method to use for the residency index.

    Wrapper method for the calulation methods above.

    @var dets - Pandas DataFrame pulled from the compressed detections CSV
    @var calculation_method - determines which method above will be used to count total time and station time
    '''
    days = 0

    if calculation_method == 'aggregate_with_overlap':
        days = aggregate_total_with_overlap(dets)
    elif calculation_method == 'aggregate_no_overlap':
        days = aggregate_total_no_overlap(dets)
    elif calculation_method == 'timedelta':
        days = total_days_diff(dets)
    else:
        days = total_days_count(dets)

    return days


def get_station_location(station, detections):
    '''
    get_station_location

    Returns the longitude and latitude of a station/receiver given the station
    and the table name.

    @var station - String that contains the station name
    @var table - the table name in which to find the station
    '''
    location = detections[detections.station == station][:1]
    location = location[['station', 'longitude', 'latitude']]
    return location


def plot_ri(ri, bounds={'north': 90, 'south': -90, 'east': 180, 'west': -180}):
    '''
    Plotting Function

    Passing the returned pandas DataFrame from the residence_index() function
    to this function will plot out the residence index

    Size, boundaries, and colors can be modified to tweek the plot.
    '''

    # Friendly message
    print 'Creating plot, please wait...',

    # Modify the plot dimensions
    fig = plt.figure(figsize=(12, 12))

    # Create the map
    map = Basemap(projection='merc',
                  resolution='f',
                  # Modify the values /to adjust the boundries of the plot
                  llcrnrlat=bounds['south'], urcrnrlat=bounds['north'],
                  llcrnrlon=bounds['west'], urcrnrlon=bounds['east'])

    # Modify the color of the water
    map.drawmapboundary(fill_color='#718ea4')

    #Modify the color of land
    map.fillcontinents(color='#2a7e43')

    # Modify the residence index coloring
    # http://scipy.github.io/old-wiki/pages/Cookbook/Matplotlib/Show_colormaps
    index_coloring = cm.Oranges

    indices = [ri['residency_index']]

    x,y = map(ri['longitude'].values, ri['latitude'].values)
    ri_map = map.scatter(x, y, s=ri['residency_index']*300, c=indices, cmap=index_coloring)
    ri_map.set_clim(0,1)
    cbar = plt.colorbar()

    print 'OK!'
    plt.show()



def interactive_map(ri_data, tileset='cartodb positron', marker_size=50, zoom=8):
    '''
    interactive_map


    Documents this!
    '''

    #create the map with a tileset, defaults to cartodb positron
    ri_map = fl.Map(location=[ri_data.latitude.median(), ri_data.longitude.median()],
                    tiles=tileset, attr='ESRI', zoom_start=zoom)

    # Add station markers to map
    for index, station in ri_data.iterrows():

        #popup string
        station_popup = "%s : %s" % (station['station'], station['residency_index'])

        # Marker creation, variables can be changed as seen fit
        fl.RegularPolygonMarker([station['latitude'],station['longitude']],
                        radius=math.ceil(station['residency_index']*marker_size),
                        fill_color='red',
                        fill_opacity=0.2,
                        color='black',
                        weight=2,
                        number_of_sides=50,
                        popup=station_popup).add_to(ri_map)
    return ri_map


def residency_index(detections, calculation_method='kessel'):

    '''
    residency_index

    This function takes in a detections CSV and determines the residency
    index for reach station.

    Residence Index (RI) was calculated as the number of days an individual
    fish was detected at each receiver station divided by the total number of
    days the fish was detected anywhere on the acoustic array. - Kessel et al.

    @var Detections - CSV Path
    '''

    detections = pd.read_csv(detections)
    dets = cp.compress_detections(detections)

    # Converting start and end date to strings
    dets['startdate'] = dets['startdate'].astype(str)
    dets['enddate'] = dets['enddate'].astype(str)

    # Remove any release locations
    dets = dets[~dets['startunqdetecid'].astype(str).str.contains("release")]

    print 'Creating the residency index using the {0} method.\nPlease be patient, I am currently working...'.format(calculation_method),

    # Determine the total days from a copy of the DataFrame
    total_days = get_days(dets.copy(), calculation_method)

    # Init the stations list
    station_list = []

    # For each unique station determine the total number of days there were detections at the station
    for station in dets['station'].unique():
        st_dets = pd.DataFrame(dets[dets['station'] == station])
        total = get_days(st_dets.copy(), calculation_method)
        location = get_station_location(station, detections)
        # Determine the RI and add the station to the list
        station_dict = {'station': station, 'days_detected': total, 'residency_index': (total/(float(total_days))),
                        'longitude': location['longitude'].values[0], 'latitude': location['latitude'].values[0]}
        station_list.append(station_dict)

    # convert the station list to a Dataframe
    all_stations = pd.DataFrame(station_list)

    # sort and reset the index for the station DataFrame
    all_stations = all_stations.sort_values(by='days_detected', ascending=False).reset_index(drop=True)

    print "OK!"
    # Return the stations RI DataFrame
    return all_stations
