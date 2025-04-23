from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from geopy.distance import geodesic

from resonate.library.exceptions import GenericException


def get_distance_matrix(detections: pd.DataFrame):
    """Creates a distance matrix of all stations in the array or line.

    Args:
        detections (pd.DataFrame): Creates a distance matrix of all stations in the array or line. 

    Returns:
        pd.DataFrame: A Pandas DataFrame matrix of station to station distances
    """
    stn_grouped = detections.groupby('station', dropna=False)
    stn_locs = stn_grouped[['longitude', 'latitude']].mean()

    dist_mtx = pd.DataFrame(
        np.zeros(len(stn_locs) ** 2).reshape(len(stn_locs), len(stn_locs)),
        index=stn_locs.index, columns=stn_locs.index)

    for cstation in dist_mtx.columns:
        for rstation in dist_mtx.index:
            cpoint = (stn_locs.loc[cstation, 'latitude'],
                      stn_locs.loc[cstation, 'longitude'])
            rpoint = (stn_locs.loc[rstation, 'latitude'],
                      stn_locs.loc[rstation, 'longitude'])
            dist_mtx.loc[rstation, cstation] = geodesic(cpoint, rpoint).m
    dist_mtx.index.name = None
    return dist_mtx


def filter_detections(detections: pd.DataFrame, suspect_file=None,
                      min_time_buffer=3600,
                      distance_matrix=False, add_column:bool=True):
    """Filters isolated detections that are more than min_time_buffer apart from
        other dets. for a series of detections in detection_file. Returns Filtered
        and Suspect dataframes.
        suspect_file can be a file of existing suspect detections to remove before
        filtering.
        dist_matrix is created as a matrix of between-station distances from
        stations defined in the input file.

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of acoustic detections
        suspect_file (str, optional): Path to a user specified suspect file, same format as 
        the detections. Defaults to None.
        min_time_buffer (int, optional): The minimum of time required for outlier detections
        in seconds. Defaults to 3600.
        distance_matrix (bool, optional):  A boolean of whether or not to generate the
        distance matrix. Defaults to False.
        add_column (bool, optional): If true, add a column to specify if the row passed the filtered 
        or not. Otherwise, split into 2 dataframes. Defaults to True.

    Raises:
        GenericException: Triggered if detections file is missing required columns for filtering.
        GenericException: Triggered if detections file is missing required columns for generating
        the distance matrix

    Returns:
        dict|pd.DataFrame: if add_column is True, a Pandas Dataframe. Otherwise, a list of Pandas DataFrames of filtered detections and suspect
        detections.
    """

    # Set of mandatory column names for detection_file
    mandatory_columns = set(['station',
                             'unqdetecid',
                             'datecollected',
                             'catalognumber'])

    # Subtract all detections found in the user defined suspect file
    if suspect_file:
        print("Found suspect file {0}. Subtracting detections from input".format(
            suspect_file))
        susp_dets = pd.read_csv(suspect_file)
        good_dets = pd.concat([detections, susp_dets], ignore_index=True)
        good_dets.drop_duplicates(mandatory_columns, keep=False, inplace=True)

    elif mandatory_columns.issubset(detections.columns):
        # calculate detections to filtered

        # For each individual catalognumber:
        # Determine the space between each detection.
        # If the space before + after > min_time_buffer
        # Remove that detection row from the detections and add it to suspect detections.
        # SQL that does this is in load_to_postgresql under createSuspect
        detections = detections.copy(deep=True)
        ind = detections['catalognumber'].unique()
        detections.loc[:, 'datecollected'] = pd.to_datetime(
            detections['datecollected'])
        user_int = timedelta(seconds=min_time_buffer)
        good_dets = pd.DataFrame()
        susp_dets = pd.DataFrame()
        grouped = detections.groupby('catalognumber', dropna=False)
        for anm in ind:
            anm_dets = grouped.get_group(anm).sort_values(
                'datecollected', ascending=True)
            intervals = anm_dets['datecollected'] - \
                anm_dets['datecollected'].shift(1)
            post_intervals = anm_dets['datecollected'].shift(
                -1) - anm_dets['datecollected']

            good_dets = pd.concat([
                good_dets, 
                anm_dets[
                    (intervals <= user_int) | (post_intervals <= user_int)
                ]
            ])

        # If they aren't a good det, they're suspect!
        # TODO: Reporting: Decide if we want to report the big 'before/after'
        # triplicate in Suspect Dets
        # If so, building susp_dets gets tougher, involves a merge and then a
        # append.
        # For now, just a matter of putting the complement of the good dets in
        # the susp_dets
        susp_dets = detections.loc[~detections['unqdetecid'].isin(
            good_dets['unqdetecid'])].copy(deep=True)

    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))

    print("Total detections in filtered dataframe: {0}".format(
        len(good_dets.index)))
    print("{0} suspect detections removed".format(len(susp_dets.index)))

    output_dict = {"filtered": good_dets, "suspect": susp_dets}

    if distance_matrix:

        # Must now have lat and long columns as well.
        dm_mandatory_columns = set(['latitude', 'longitude'])
        if dm_mandatory_columns.issubset(detections.columns):
            output_dict['dist_mtrx'] = get_distance_matrix(detections)
            print("There are {0} station locations in the distance \
                matrix".format(len(output_dict['dist_mtrx'].index)))
        else:
            raise GenericException("Missing required input columns for \
                distance matrix calc: {}".format(
                dm_mandatory_columns - set(detections.columns)))
    if add_column:
        output_dict['filtered'].loc[:, 'passed_detection_filter'] = True
        output_dict['suspect'].loc[output_dict['suspect'].index, 'passed_detection_filter'] = False
        output_df = pd.concat(output_dict.values()).reset_index(drop=True)
        if distance_matrix:
            return {'detections': output_df, 'dist_mtrx': output_dict['dist_mtrx']}
        else:
            return output_df


    return output_dict


def distance_filter(detections: pd.DataFrame, maximum_distance=100000, add_column:bool=True):
    """Filters detections based on distance between detections.

    Args:
        detections (pd.DataFrame): a Pandas DataFrame of acoustic detection
        maximum_distance (int, optional): a number in meters. Defaults to 100000.
        add_column (bool, optional): If true, add a column to specify if the row passed the filtered 
        or not. Otherwise, split into 2 dataframes. Defaults to True.

    Raises:
        GenericException: Triggered if detections file is missing required columns

    Returns:
        dict|pd.DataFrame: if add_column is True, a Pandas Dataframe. Otherwise, a list of Pandas DataFrames of filtered detections and suspect
        detections.
    """
    pd.options.mode.chained_assignment = None

    mandatory_columns = set(['station',
                             'unqdetecid',
                             'datecollected',
                             'catalognumber'])

    if mandatory_columns.issubset(detections.columns):
        dm = get_distance_matrix(detections)

        lead_lag_stn_df = pd.DataFrame()
        for _, group in detections.sort_values(['datecollected']).groupby(['catalognumber'], dropna=False):
            group['lag_station'] = group.station.shift(1).fillna(group.station)
            group['lead_station'] = group.station.shift(
                -1).fillna(group.station)
            lead_lag_stn_df = pd.concat([lead_lag_stn_df, group])
        del detections

        distance_df = pd.DataFrame()
        for _, group in lead_lag_stn_df.groupby(['station', 'lag_station', 'lead_station'], dropna=False):
            stn = group.station.unique()[0]
            lag_stn = group.lag_station.unique()[0]
            lead_stn = group.lead_station.unique()[0]
            lag_distance = dm.loc[stn, lag_stn]
            lead_distance = dm.loc[stn, lead_stn]
            group['lag_distance_m'] = lag_distance
            group['lead_distance_m'] = lead_distance
            distance_df = pd.concat([distance_df, group])
        del lead_lag_stn_df
        distance_df.sort_index(inplace=True)
        if add_column:
            distance_df['passed_distance_filter'] = (distance_df.lag_distance_m <= maximum_distance) & (distance_df.lead_distance_m <= maximum_distance)
            return distance_df
        else:
            filtered_detections = dict()
            filtered_detections['filtered'] = distance_df[(distance_df.lag_distance_m <= maximum_distance) & (
                distance_df.lead_distance_m <= maximum_distance)].reset_index(drop=True)
            filtered_detections['suspect'] = distance_df[(distance_df.lag_distance_m > maximum_distance) | (
                distance_df.lead_distance_m > maximum_distance)].reset_index(drop=True)
            return filtered_detections
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))


def velocity_filter(detections: pd.DataFrame, maximum_velocity=10,  add_column:bool=True):
    """Filters detections based on the time it took to travel between locations.

    Args:
        detections (pd.DataFrame):  a Pandas DataFrame of acoustic detection
        maximum_velocity (int, optional): The maximum velocity the animals can travel. Defaults to 10.
        add_column (bool, optional): If true, add a column to specify if the row passed the filtered 
        or not. Otherwise, split into 2 dataframes. Defaults to True.

    Raises:
        GenericException: Triggered if detections file is missing required columns

    Returns:
        dict|pd.DataFrame: if add_column is True, a Pandas Dataframe. Otherwise, a dict of Pandas DataFrames of filtered detections and suspect
        detections.
    """
    pd.options.mode.chained_assignment = None

    mandatory_columns = set(['station',
                             'unqdetecid',
                             'datecollected',
                             'catalognumber'])

    if mandatory_columns.issubset(detections.columns):

        dm = get_distance_matrix(detections)

        lead_lag_df = pd.DataFrame()
        for _, group in detections.sort_values(['datecollected']).groupby(['catalognumber'], dropna=False):
            group['lag_station'] = group.station.shift(1).fillna(group.station)
            group['lead_station'] = group.station.shift(
                -1).fillna(group.station)

            group.datecollected = pd.to_datetime(group.datecollected)
            group['lag_time_diff'] = group.datecollected.diff().fillna(
                timedelta(seconds=1))
            group['lead_time_diff'] = group.lag_time_diff.shift(
                -1).fillna(timedelta(seconds=1))
            lead_lag_df = pd.concat([lead_lag_df, group])
        del detections

        vel_df = pd.DataFrame()
        for _, group in lead_lag_df.groupby(['station', 'lag_station', 'lead_station'], dropna=False):
            stn = group.station.unique()[0]
            lag_stn = group.lag_station.unique()[0]
            lead_stn = group.lead_station.unique()[0]

            lag_distance = dm.loc[stn, lag_stn]
            lead_distance = dm.loc[stn, lead_stn]

            group['lag_distance_m'] = lag_distance
            group['lead_distance_m'] = lead_distance
            vel_df = pd.concat([vel_df, group])
        del lead_lag_df
        vel_df['lag_velocity'] = vel_df.lag_distance_m / \
            vel_df.lag_time_diff.dt.total_seconds()
        vel_df['lead_velocity'] = vel_df.lead_distance_m / \
            vel_df.lead_time_diff.dt.total_seconds()
        vel_df.sort_index(inplace=True)
        if add_column:
            vel_df['passed_velocity_filter'] = (
                (vel_df.lag_velocity <= maximum_velocity) &
                (vel_df.lead_velocity <= maximum_velocity) & 
                (vel_df.lag_velocity.notna()) & vel_df.lag_velocity.notna())
            return vel_df
        else:
            filtered_detections = dict()
            filtered_detections['filtered'] = vel_df[(vel_df.lag_velocity <= maximum_velocity) & (
                vel_df.lead_velocity <= maximum_velocity)].reset_index(drop=True)
            filtered_detections['suspect'] = vel_df[
                (vel_df.lag_velocity > maximum_velocity) |
                (vel_df.lead_velocity > maximum_velocity) |
                (vel_df.lag_velocity.isna()) |
                (vel_df.lead_velocity.isna())
            ].reset_index(drop=True)
            return filtered_detections
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))


def filter_all(detections: pd.DataFrame, min_time_buffer=3600, maximum_distance=100000, maximum_velocity=10):
    """Runs all 3 filters on a given detection dataframe, returning 1 dataframe with 3 columns specifying
        if the row passed each filter test. Does not return a distance matrix.

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of acoustic detections
        min_time_buffer (int, optional): The minimum of time required for outlier detections
        in seconds. Defaults to 3600.
        maximum_distance (int, optional): a number in meters. Defaults to 100000.
        maximum_velocity (int, optional): The maximum velocity the animals can travel. Defaults to 10.

    Raises:
        GenericException: Triggered if detections file is missing required columns

    Returns:
        pd.DataFrame: A dataframe with all 3 filter columns added and populated
    """
    # Set of mandatory column names for detection_file
    mandatory_columns = set(['station',
                             'unqdetecid',
                             'datecollected',
                             'catalognumber'])
    if mandatory_columns.issubset(detections.columns):
        detections = detections.copy(deep=True)
        detections = filter_detections(detections, min_time_buffer=min_time_buffer)
        detections = distance_filter(detections, maximum_distance=maximum_distance)
        detections = velocity_filter(detections, maximum_velocity=maximum_velocity)
        return detections
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))

    