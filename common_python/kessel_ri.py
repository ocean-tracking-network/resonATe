import pandas as pd
from datetime import datetime
import common_python.compress as cp
from library import pg_connection as pg
import os
import re

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

'''
total_days_diff()
-----------------
The function below determines the total days difference.

The difference is determined
by the minimal startdate of every detection and the maximum enddate of every detection.
Both are converted into a datetime then subtracted to get a timedelta. The timedelta
is converted to seconds and divided by the number of seconds in a day (86400). The function
returns a floating point number of days (i.e. 503.76834).

@var Detections - Pandas DataFrame pulled from the compressed detections CSV
'''


def total_days_diff(detections):
    first = datetime.strptime(detections.startdate.min(), "%Y-%m-%d %H:%M:%S")
    last = datetime.strptime(detections.enddate.max(), "%Y-%m-%d %H:%M:%S")
    total = last - first
    total = total.total_seconds()/86400.0
    return total


'''
total_days_count()
------------------
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


def total_days_count(detections):
    detections['startdate'] = detections['startdate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",)).apply(datetime.date)
    detections['enddate'] = detections['enddate'].apply(datetime.strptime, args=("%Y-%m-%d %H:%M:%S",)).apply(datetime.date)
    detections = pd.unique(detections[['startdate', 'enddate']].values.ravel())
    return detections.size


'''
aggregate_total_with_overlap()
----------------------------------------

The function below aggregates timedelta of startdate and enddate of each detection into
a final timedelta then returns a float of the number of days. If the startdate and enddate
are the same, a timedelta of one second is assumed.

@var Detections - Pandas DataFrame pulled from the compressed detections CSV
'''


def aggregate_total_with_overlap(detections):
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


'''
aggregate_total_no_overlap()
--------------------------------------

The function below aggregates timedelta of startdate and enddate, excluding overlap between
detections. Any overlap between two detections is converted to a new detection using the earlier
startdate and the latest enddate. If the startdate and enddate are the same, a timedelta of one
second is assumed.

@var Detections - Pandas DataFrame pulled from the compressed detections CSV
'''


def aggregate_total_no_overlap(detections):
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


'''
get_days()
----------

Determines which calculation method to use for the residency index.

Wrapper method for the calulation methods above.

@var dets - Pandas DataFrame pulled from the compressed detections CSV
@var calculation_method - determines which method above will be used to count total time and station time
'''


def get_days(dets, calculation_method='kessel'):
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


'''
get_station_location()
----------------------

Returns the longitude and latitude of a station/receiver given the station
and the table name.

@var station - String that contains the station name
@var table - the table name in which to find the station
'''


def get_station_location(station, table):
    db = pg.get_engine()
    location = pd.read_sql("SELECT * FROM "+table+" WHERE station = %(station)s LIMIT 1", db, params={"station": station})
    location = location[['station', 'longitude', 'latitude']]
    location[['longitude', 'latitude']] = location[['longitude', 'latitude']].astype(float)
    location[['station']] = location[['station']].astype(str)
    return location.loc[0].to_dict()


'''
residency_index()
-----------------

This function takes in a commpressed detections CSV and determines the residency
index for reach station.

Residence Index (RI) was calculated as the number of days an individual fish was
detected at each receiver station divided by the total number of days the fish was
detected anywhere on the acoustic array. - Kessel et al.

@var Detections - CSV Path
'''

def residency_index(detections, calculation_method='kessel'):
    # Create a DataFrame from the CSV
    full_path_detections = "%s%s" % (DATADIRECTORY, detections)
    dets = pd.read_csv(full_path_detections)

    tblname = 'vsisscratch'

    if not (set(['startdate', 'enddate', 'station']).issubset(dets.columns)):
        cmpr_detections = cp.CompressDetections(detections, createfile=False, tablename = tblname)
        db = pg.get_engine()
        dets = pd.read_sql_table('mv_anm_compressed',  db)


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

        location = get_station_location(station, tblname)
        # Determine the RI and add the station to the list
        station_dict = {'station': station, 'days_detected': total, 'residency_index': (total/(float(total_days))), 'longitude': location['longitude'], 'latitude': location['latitude']}
        station_list.append(station_dict)

    # convert the station list to a Dataframe
    all_stations = pd.DataFrame(station_list)

    # sort and reset the index for the station DataFrame
    all_stations = all_stations.sort_values(by='days_detected', ascending=False).reset_index(drop=True)

    print "OK!"
    # Write a new CSV file for the RI
    print 'Source file was %s' % full_path_detections
    p = re.compile(r"_v(\d\d)\.csv") # capture and retain version if version exists.
    if p.search(full_path_detections): # if there's a capture group (ie there was a version number)
        new_ri_detections = p.sub(r'_%s_ri_v\1.csv' % calculation_method, full_path_detections)
    else:
        new_ri_detections = re.sub('\.csv', '_%s_ri.csv' % calculation_method, full_path_detections)
    print "Writing residence index CSV to "+new_ri_detections+" ..."
    all_stations.to_csv(new_ri_detections)
    print "OK!"
    # Return the stations RI DataFrame
    return all_stations