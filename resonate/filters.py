from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from geopy.distance import geodesic
from resonate.library.exceptions import GenericException


def get_distance_matrix(detections):
    """
    Creates a distance matrix of all stations in the array or line.

    :param detections: a Pandas DataFrame of detections

    :return: A Pandas DataFrame matrix of station to station distances

    """
    stn_grouped = detections.groupby('station')
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


def filter_detections(detections, suspect_file=None,
                      min_time_buffer=3600,
                      distance_matrix=False):
    """
    Filters isolated detections that are more than min_time_buffer apart from
    other dets. for a series of detections in detection_file. Returns Filtered
    and Suspect dataframes.
    suspect_file can be a file of existing suspect detections to remove before
    filtering.
    dist_matrix is created as a matrix of between-station distances from
    stations defined in the input file.

    :param detections: A Pandas DataFrame of acoustic detections

    :param suspect_file: Path to a user specified suspect file, same format as the detections

    :param min_time_buffer: The minimum of time required for outlier detections
        in seconds

    :param distance_matrix: A boolean of whether or not to generate the
        distance matrix

    :return: A list of Pandas DataFrames of filtered detections, suspect
        detections, and a distance matrix

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

        ind = detections['catalognumber'].unique()
        detections['datecollected'] = pd.to_datetime(
            detections['datecollected'])
        user_int = timedelta(seconds=min_time_buffer)
        good_dets = pd.DataFrame()
        susp_dets = pd.DataFrame()
        grouped = detections.groupby('catalognumber')
        for anm in ind:
            anm_dets = grouped.get_group(anm)
            intervals = anm_dets['datecollected'] - \
                anm_dets['datecollected'].shift(1)
            post_intervals = anm_dets['datecollected'].shift(
                -1) - anm_dets['datecollected']

            good_dets = good_dets.append(
                anm_dets[
                    (intervals <= user_int) | (post_intervals <= user_int)
                ]
            )

        # If they aren't a good det, they're suspect!
        # TODO: Reporting: Decide if we want to report the big 'before/after'
        # triplicate in Suspect Dets
        # If so, building susp_dets gets tougher, involves a merge and then a
        # append.
        # For now, just a matter of putting the complement of the good dets in
        # the susp_dets
        susp_dets = detections[~detections['unqdetecid'].isin(
            good_dets['unqdetecid'])]

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

    return output_dict


def distance_filter(detections, maximum_distance=100000):
    """
    :param detections: a Pandas DataFrame of acoustic detection
    :param maximum_distance: a umber in meters, default is 100000

    :return: A list of Pandas DataFrames of filtered detections and suspect
        detections
    """
    pd.options.mode.chained_assignment = None

    mandatory_columns = set(['station',
                             'unqdetecid',
                             'datecollected',
                             'catalognumber'])

    if mandatory_columns.issubset(detections.columns):
        dm = get_distance_matrix(detections)

        lead_lag_stn_df = pd.DataFrame()

        for index, group in detections.sort_values(['datecollected']).groupby(['catalognumber']):
            group['lag_station'] = group.station.shift(1).fillna(group.station)
            group['lead_station'] = group.station.shift(
                -1).fillna(group.station)
            lead_lag_stn_df = lead_lag_stn_df.append(group)

        del detections

        distance_df = pd.DataFrame()

        for index, group in lead_lag_stn_df.groupby(['station', 'lag_station', 'lead_station']):
            stn = group.station.unique()[0]
            lag_stn = group.lag_station.unique()[0]
            lead_stn = group.lead_station.unique()[0]
            lag_distance = dm.loc[stn, lag_stn]
            lead_distance = dm.loc[stn, lead_stn]
            group['lag_distance_m'] = lag_distance
            group['lead_distance_m'] = lead_distance
            distance_df = distance_df.append(group)

        del lead_lag_stn_df
        distance_df.sort_index(inplace=True)

        filtered_detections = dict()
        filtered_detections['filtered'] = distance_df[(distance_df.lag_distance_m <= maximum_distance) & (
            distance_df.lead_distance_m <= maximum_distance)].reset_index(drop=True)
        filtered_detections['suspect'] = distance_df[(distance_df.lag_distance_m > maximum_distance) | (
            distance_df.lead_distance_m > maximum_distance)].reset_index(drop=True)
        return filtered_detections
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))


def velocity_filter(detections, maximum_velocity=10):
    """
    :param detections:
    :param maximum_velocity:

    :return: A list of Pandas DataFrames of filtered detections and suspect
        detections
    """
    pd.options.mode.chained_assignment = None

    mandatory_columns = set(['station',
                             'unqdetecid',
                             'datecollected',
                             'catalognumber'])

    if mandatory_columns.issubset(detections.columns):

        dm = get_distance_matrix(detections)

        lead_lag_df = pd.DataFrame()

        for index, group in detections.sort_values(['datecollected']).groupby(['catalognumber']):
            group['lag_station'] = group.station.shift(1).fillna(group.station)
            group['lead_station'] = group.station.shift(
                -1).fillna(group.station)

            group.datecollected = pd.to_datetime(group.datecollected)
            group['lag_time_diff'] = group.datecollected.diff().fillna(
                timedelta(seconds=1))
            group['lead_time_diff'] = group.lag_time_diff.shift(
                -1).fillna(timedelta(seconds=1))

            lead_lag_df = lead_lag_df.append(group)

        del detections

        vel_df = pd.DataFrame()
        for index, group in lead_lag_df.groupby(['station', 'lag_station', 'lead_station']):
            stn = group.station.unique()[0]
            lag_stn = group.lag_station.unique()[0]
            lead_stn = group.lead_station.unique()[0]

            lag_distance = dm.loc[stn, lag_stn]
            lead_distance = dm.loc[stn, lead_stn]

            group['lag_distance_m'] = lag_distance
            group['lead_distance_m'] = lead_distance
            vel_df = vel_df.append(group)

        del lead_lag_df

        vel_df['lag_velocity'] = vel_df.lag_distance_m / \
            vel_df.lag_time_diff.dt.total_seconds()
        vel_df['lead_velocity'] = vel_df.lead_distance_m / \
            vel_df.lead_time_diff.dt.total_seconds()
        vel_df.sort_index(inplace=True)
        filtered_detections = dict()
        filtered_detections['filtered'] = vel_df[(vel_df.lag_velocity <= maximum_velocity) & (
            vel_df.lead_velocity <= maximum_velocity)].reset_index(drop=True)
        filtered_detections['suspect'] = vel_df[(vel_df.lag_velocity > maximum_velocity) | (
            vel_df.lead_velocity > maximum_velocity)].reset_index(drop=True)
        return filtered_detections
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))
