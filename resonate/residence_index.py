import math
from datetime import datetime

import pandas as pd
import plotly.graph_objs as go
import plotly.offline as py
import resonate.compress as cp


def total_days_diff(detections: pd.DataFrame):
    """Determines the total days difference.

    The difference is determined
    by the minimal startdate of every detection and the maximum enddate of
    every detection. Both are converted into a datetime then subtracted to
    get a timedelta. The timedelta is converted to seconds and divided by
    the number of seconds in a day (86400). The function returns a floating
    point number of days (i.e. 503.76834).

    Args:
        detections (pd.DataFrame):  Pandas DataFrame pulled from the compressed detections CSV


    Returns:
        float: An float in the number of days
    """
    
    first = datetime.strptime(detections.startdate.min(), "%Y-%m-%d %H:%M:%S")
    last = datetime.strptime(detections.enddate.max(), "%Y-%m-%d %H:%M:%S")
    total = last - first
    total = total.total_seconds() / 86400.0
    return total


def total_days_count(detections: pd.DataFrame):
    """The function below takes a Pandas DataFrame and determines the number of days any
    detections were seen on the array.

    The function converst both the startdate and enddate columns into a date with no hours, minutes,
    or seconds. Next it creates a list of the unique days where a detection was seen. The size of the
    list is returned as the total number of days as an integer.

    *** NOTE ****
    Possible rounding error may occur as a detection on 2016-01-01 23:59:59 and a detection on
    2016-01-02 00:00:01 would be counted as days when it is really 2-3 seconds.

    Args:
        detections (pd.DataFrame): Pandas DataFrame pulled from the compressed detections CSV

    Returns:
        int: An int in the number of days
    """
    
    detections['startdate'] = detections['startdate'].apply(
        datetime.strptime, args=("%Y-%m-%d %H:%M:%S",)).apply(datetime.date)
    detections['enddate'] = detections['enddate'].apply(
        datetime.strptime, args=("%Y-%m-%d %H:%M:%S",)).apply(datetime.date)
    detections = pd.unique(detections[['startdate', 'enddate']].values.ravel())
    return detections.size


def aggregate_total_with_overlap(detections: pd.DataFrame):
    """The function below aggregates timedelta of startdate and enddate of each detection into
    a final timedelta then returns a float of the number of days. If the startdate and enddate
    are the same, a timedelta of one second is assumed.

    Args:
        detections (pd.DataFrame): Pandas DataFrame pulled from the compressed detections CSV

    Returns:
        float: An float in the number of days
    """
    
    total = pd.Timedelta(0)
    detections['startdate'] = detections['startdate'].apply(
        datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))
    detections['enddate'] = detections['enddate'].apply(
        datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))
    detections['timedelta'] = detections['enddate'] - detections['startdate']

    for index, row in detections.iterrows():
        if row['timedelta'] > pd.Timedelta(0):
            diff = row['timedelta']
        else:
            diff = pd.Timedelta('1 second')
        total += diff
    return total.total_seconds() / 86400.0


def aggregate_total_no_overlap(detections: pd.DataFrame):
    """The function below aggregates timedelta of startdate and enddate, excluding overlap between
    detections. Any overlap between two detections is converted to a new detection using the earlier
    startdate and the latest enddate. If the startdate and enddate are the same, a timedelta of one
    second is assumed.

    Args:
        detections (pd.DataFrame): pandas DataFrame pulled from the compressed detections CSV

    Returns:
        float: An float in the number of days
    """
    
    total = pd.Timedelta(0)

    # sort and convert datetimes
    detections = detections.sort_values(
        by='startdate', ascending=False).reset_index(drop=True)
    detections['startdate'] = detections['startdate'].apply(
        datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))
    detections['enddate'] = detections['enddate'].apply(
        datetime.strptime, args=("%Y-%m-%d %H:%M:%S",))

    # A stack is used as an easy way to organize and maintain the detections
    detection_stack = list(detections.T.to_dict().values())

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
                diff += current_time_block['enddate'] - \
                    current_time_block['startdate']
                if diff == pd.Timedelta(0):
                    diff = pd.Timedelta('1 second')
                total += diff

                # Add the next block back into the stack so that it can be used in the next iteration
                detection_stack.append(next_time_block)
            else:

                # If there is overlap take a new endate, eliminating the overlap, and add it back into the stack for the next iteration
                current_time_block['enddate'] = max(
                    [current_time_block['enddate'], next_time_block['enddate']])
                detection_stack.append(current_time_block)

    # Return the value as a float in days
    return total.total_seconds() / 86400.0


def get_days(dets: pd.DataFrame, calculation_method='kessel'):
    """Determines which calculation method to use for the residency index.

    Wrapper method for the calulation methods above.

    Args:
        dets (pd.DataFrame): A Pandas DataFrame pulled from the compressed detections CSV
        calculation_method (str, optional): determines which method above will be used to
        count total time and station time. Defaults to 'kessel'.

    Returns:
        int: An int in the number of days
    """
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


def get_station_location(station: str, detections: pd.DataFrame):
    """Returns the longitude and latitude of a station/receiver given the station
    and the table name.

    Args:
        station (str): String that contains the station name
        detections (pd.DataFrame): the table name in which to find the station

    Returns:
        pd.DataFrame: A Pandas DataFrame of station, latitude, and longitude
    """
    location = detections[detections.station == station][:1]
    location = location[['station', 'longitude', 'latitude']]
    return location


def plot_ri(ri_data: pd.DataFrame, ipython_display=True,
            title='Bubble Plot', height=700,
            width=1000, plotly_geo=None, filename=None,
            marker_size=6, scale_markers=False,
            colorscale='Viridis', mapbox_token=None):
    """Creates a bubble plot of residency index data.

    Args:
        ri_data (pd.DataFrame): A Pandas DataFrame generated from ``residency_index()``
        ipython_display (bool, optional): a boolean to show in a notebook. Defaults to True.
        title (str, optional): the title of the plot. Defaults to 'Bubble Plot'.
        height (int, optional): the height of the plotly. Defaults to 700.
        width (int, optional): the width of the plotly. Defaults to 1000.
        plotly_geo (dict, optional): an optional dictionary to control the
        geographic aspects of the plot. Defaults to None.
        filename (str, optional): Plotly filename to write to. Defaults to None.
        marker_size (int, optional): An int to indicate the diameter in pixels. Defaults to 6.
        scale_markers (bool, optional): A boolean to indicate whether or not markers are
        scaled by their value. Defaults to False.
        colorscale (str, optional): A string to indicate the color index. See here for options:
        https://community.plot.ly/t/what-colorscales-are-available-in-plotly-and-which-are-the-default/2079. Defaults to 'Viridis'.
        mapbox_token (str, optional): A string of mapbox access token. Defaults to None.

    Returns:
        (None|Any): A plotly geoscatter or None if ipython_display is True
    """
    
    ri_data = ri_data.sort_values('residency_index')

    map_type = 'scattergeo'

    if mapbox_token is not None:
        map_type = 'scattermapbox'
        mapbox = dict(
            accesstoken=mapbox_token,
            center=dict(
                lon=ri_data.longitude.mean(),
                lat=ri_data.latitude.mean()
            ),
            zoom=5,
            style='light'
        )

    if scale_markers:
        marker_size = (ri_data.residency_index * marker_size + 5).tolist()
    else:
        marker_size += 5
    data = [
        {
            'lon': ri_data.longitude.tolist(),
            'lat': ri_data.latitude.tolist(),
            'text': ri_data.station + " : " + ri_data.residency_index.astype(str),
            'mode': 'markers',
            'marker': {
                'color': ri_data.residency_index.tolist(),
                'size': marker_size,
                'showscale': True,
                'colorscale': colorscale,
                'colorbar': {
                    'title': 'Detection Count'
                }
            },
            'type': map_type
        }
    ]

    if plotly_geo is None:
        plotly_geo = dict(
            showland=True,
            landcolor="rgb(255, 255, 255)",
            showocean=True,
            oceancolor="rgb(212,212,212)",
            showlakes=True,
            lakecolor="rgb(212,212,212)",
            showrivers=True,
            rivercolor="rgb(212,212,212)",
            resolution=50,
            showcoastlines=False,
            showframe=False,
            projection=dict(
                type='mercator',
            )
        )
    plotly_geo.update(
        center=dict(
            lon=ri_data.longitude.mean(),
            lat=ri_data.latitude.mean()
        ),
        lonaxis=dict(
            range=[ri_data.longitude.min(), ri_data.longitude.max()],
        ),
        lataxis=dict(
            range=[ri_data.latitude.min(), ri_data.latitude.max()],
        )
    )

    if mapbox_token is None:
        layout = dict(
            geo=plotly_geo,
            title=title
        )
    else:
        layout = dict(title=title,
                      autosize=True,
                      hovermode='closest',
                      mapbox=mapbox
                      )

    if ipython_display:
        layout.update(
            height=height,
            width=width
        )
        fig = {'data': data, 'layout': layout}

        py.init_notebook_mode()
        return py.iplot(fig)
    else:
        fig = {'data': data, 'layout': layout}
        return py.plot(fig, filename=filename)


def residency_index(detections: pd.DataFrame, calculation_method='kessel'):
    """This function takes in a detections CSV and determines the residency
    index for reach station.

    Residence Index (RI) was calculated as the number of days an individual
    fish was detected at each receiver station divided by the total number of
    days the fish was detected anywhere on the acoustic array. - Kessel et al.


    Args:
        detections (pd.DataFrame): Dataframe of detections
        calculation_method (str, optional): determines which method above will be used to
        count total time and station time. Defaults to 'kessel'.

    Returns:
        pd.DataFrame: A residence index DataFrame with the following columns
            * days_detected
            * latitude
            * longitude
            * residency_index
            * station
    """
    dets = cp.compress_detections(detections)

    # Converting start and end date to strings
    dets['startdate'] = dets['startdate'].astype(str)
    dets['enddate'] = dets['enddate'].astype(str)

    # Remove any release locations
    dets = dets[~dets['startunqdetecid'].astype(str).str.contains("release")]

    print('Creating the residency index using the {0} method.\nPlease be patient, I am currently working...'.format(
        calculation_method))

    # Determine the total days from a copy of the DataFrame
    total_days = get_days(dets.copy(), calculation_method)

    # Init the stations list
    station_list = []

    # For each unique station determine the total number of days there were
    # detections at the station
    for station in dets['station'].unique():
        st_dets = pd.DataFrame(dets[dets['station'] == station])
        total = get_days(st_dets.copy(), calculation_method)
        location = get_station_location(station, detections)
        # Determine the RI and add the station to the list
        station_dict = {
            'days_detected': total, 
            'latitude': location['latitude'].values[0],
            'longitude': location['longitude'].values[0], 
            'residency_index': (total / (float(total_days))),
            'station': station,
        } 
        station_list.append(station_dict)

    # convert the station list to a Dataframe
    all_stations = pd.DataFrame(station_list)

    # sort and reset the index for the station DataFrame
    all_stations = all_stations.sort_values(
        by='days_detected', ascending=False).reset_index(drop=True)

    print("OK!")
    # Return the stations RI DataFrame
    return all_stations
