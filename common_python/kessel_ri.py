import pandas as pd
from datetime import datetime

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
residency_index()
-----------------

This function takes in a commpressed detections CSV and determ,ines the residency
index for reach station.

Residence Index (RI) was calculated as the number of days an individual fish was
detected at each receiver station divided by the total number of days the fish was
detected anywhere on the acoustic array. - Kessel et al.

@var Detections - CSV Path
'''


def residency_index(detections):

    # Create a DataFrame from the CSV
    dets = pd.read_csv(detections)

    # Remove any release locations
    dets = dets[~dets['startunqdetecid'].str.contains("release")]

    # Determine the total days from a copy of the DataFrame
    total_days = total_days_count(dets.copy())

    # Init the stations list
    station_list = []

    # For each unique station determine the total number of days there were detections at the station
    for station in dets['station'].unique():
        st_dets = pd.DataFrame(dets[dets['station'] == station])
        total = total_days_count(st_dets.copy())

        # Determine the RI and add the station to the list
        station_dict = {'station':station, 'days_detected':total, 'residency_index':(total/(float(total_days)))}
        station_list.append(station_dict)

    # convert the station list to a Dataframe
    all_stations = pd.DataFrame(station_list)

    # sort and reset the index for the station DataFrame
    all_stations = all_stations.sort_values(['days_detected'], ascending=False).reset_index(drop=True)

    # Write a new CSV file for the RI
    new_ri_detections = detections.replace('_v00.csv', '_ri_v00.csv')
    all_stations.to_csv(new_ri_detections)

    # Return the stations RI DataFrame
    return all_stations
