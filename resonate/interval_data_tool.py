import pandas as pd
import geopy

def interval_data(compressed_df, dist_matrix_df, station_radius_df=None):
    """
    Creates a detection interval file from a compressed detection, distance matrix and station detection radius DataFrames

    :param compressed_df: compressed detection dataframe
    :param dist_matrix_df: station distance matrix dataframe
    :param station_radius: station distance radius dataframe
    :return: interval detection Dataframe
    """

    # Create two dataframes from input compressed detections and decrement the second's seq_num
    fst = compressed_df[
        ['catalognumber', 'station', 'seq_num', 'total_count', 'startdate', 'enddate', 'endunqdetecid']].copy()
    snd = compressed_df[
        ['catalognumber', 'station', 'seq_num', 'total_count', 'startdate', 'enddate', 'endunqdetecid']].copy()
    snd.seq_num -= 1

    # Rename columns
    fst.columns = ['catalognumber', 'from_station', 'seq_num', 'from_detcnt',
                   'from_arrive', 'from_leave', 'unqdetid_from']
    snd.columns = ['catalognumber', 'to_station', 'seq_num', 'to_detcnt',
                   'to_arrive', 'to_leave', 'unqdetid_arrive']

    # Merge the two DataFrames together linking catalognumber and seq_num
    merged = pd.merge(fst, snd, how='left', on=['catalognumber', 'seq_num'])

    # Create additional column placeholders
    merged['intervaltime'] = None
    merged['intervalseconds'] = None
    merged['distance_m'] = None
    merged['metres_per_second'] = None

    # Loop through all rows linking distance matrices and calculating average speed between intervals
    for idx, item in merged.iterrows():
        # If any of the station pairs don't exist, skip processing current row
        if not (pd.isnull(item['from_station']) or pd.isnull(item['to_station'])):
            # Get station matrix distance (input in km)
            matrix_distance_km = dist_matrix_df.loc[item['from_station'], item['to_station']]

            # If matrix pair exists do distance calculations
            if matrix_distance_km:
                if isinstance(station_radius_df, pd.DataFrame):
                    stn1_radius = station_radius_df.loc[item['from_station'], 'radius']
                    stn2_radius = station_radius_df.loc[item['to_station'], 'radius']

                    distance = max(geopy.distance.Distance(0).km, matrix_distance_km - stn1_radius.km - stn2_radius.km)*1000
                else:
                    distance = max(geopy.distance.Distance(0).km, matrix_distance_km)*1000

                merged.loc[idx, 'distance_m'] =  distance

                time_interval = item['to_arrive'] - item['from_leave']
                merged.loc[idx, 'intervaltime'] =  time_interval
                merged.loc[idx, 'intervalseconds'] = time_interval.total_seconds()

                if time_interval.seconds != 0:
                    merged.loc[idx, 'metres_per_second']= distance / time_interval.seconds

    return merged
