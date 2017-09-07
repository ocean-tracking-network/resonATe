import pandas as pd
import datetime
import numpy as np
from geopy.distance import vincenty
from library.exceptions import GenericException


def get_distance_matrix(detectiondf):

    """
    Creates a distance matrix of all stations in the array or line.

    :param detectiondf: a Pandas DataFrame of detections

    :return: A Pandas DataFrame matrix of station to station distances

    """
    def get_v_distance(col):
        end = stn_locs.ix[col.name]['coords']
        return stn_locs['coords'].apply(vincenty, args=(end,), ellipsoid='WGS-84')

    stn_grouped = detectiondf.groupby('station')
    stn_locs = stn_grouped[['longitude', 'latitude']].mean()
    stn_locs['coords'] = zip(stn_locs.latitude, stn_locs.longitude)

    dist_mtx = pd.DataFrame(
        np.zeros(len(stn_locs) ** 2).reshape(len(stn_locs), len(stn_locs)),
        index=stn_locs.index, columns=stn_locs.index).apply(get_v_distance, axis=1).T
    dist_mtx.index.name = None
    return dist_mtx


def filter_detections(detection_file, suspect_file=None,
                      detection_radius=None, min_time_buffer=60,
                      distance_matrix=False):

    """
    Filters isolated detections that are more than min_time_buffer apart from
    other dets. for a series of detections in detection_file. Returns Filtered
    and Suspect dataframes.
    suspect_file can be a file of existing suspect detections to remove before
    filtering.
    dist_matrix is created as a matrix of between-station distances from
    stations defined in the input file.

    :param detection_file: A CSV file of acoustic detections

    :param suspect_file: Path to a user specified suspect file

    :param detection_radius:

    :param min_time_buffer: The minimum of time required for outlier detections in
        minutes

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

    # Load the file into a dataframe
    df = pd.read_csv(detection_file)

    # Subtract all detections found in the user defined suspect file
    if suspect_file:
        print "Found suspect file {0}. Subtracting detections from input".format(suspect_file)
        susp_dets = pd.read_csv(suspect_file)
        good_dets = pd.concat([df, susp_dets], ignore_index=True)
        good_dets.drop_duplicates(mandatory_columns, keep=False, inplace=True)

    elif mandatory_columns.issubset(df.columns):
        # calculate detections to filtered

        # For each individual catalognumber:
        # Determine the space between each detection.
        # If the space before + after > min_time_buffer
        # Remove that detection row from the df and add it to suspect df.
        # SQL that does this is in load_to_postgresql under createSuspect

        ind = df['catalognumber'].unique()
        df['datecollected'] = pd.to_datetime(df['datecollected'])
        user_int = datetime.timedelta(minutes=min_time_buffer)
        good_dets = pd.DataFrame()
        susp_dets = pd.DataFrame()
        grouped = df.groupby('catalognumber')
        for anm in ind:
            anm_dets = grouped.get_group(anm)
            intervals = anm_dets['datecollected'] - anm_dets['datecollected'].shift(1)
            post_intervals = anm_dets['datecollected'].shift(-1) - anm_dets['datecollected']


            good_dets = good_dets.append(anm_dets[(intervals <= user_int) | (post_intervals <= user_int)])

        # If they aren't a good det, they're suspect!
        # TODO: Reporting: Decide if we want to report the big 'before/after' triplicate in Suspect Dets
        # If so, building susp_dets gets tougher, involves a merge and then a append.
        # For now, just a matter of putting the complement of the good dets in the susp_dets
        susp_dets = df[~df['unqdetecid'].isin(good_dets['unqdetecid'])]

    else:
        raise GenericException("Missing required input columns: {}".format(mandatory_columns - set(df.columns)))

    print "Total detections in filtered dataframe: {0}".format(len(good_dets.index))
    print "{0} suspect detections removed".format(len(susp_dets.index))

    output_dict = {"filtered": good_dets, "suspect": susp_dets}

    if distance_matrix:

        # Must now have lat and long columns as well.
        dm_mandatory_columns = set(['latitude', 'longitude'])
        if dm_mandatory_columns.issubset(df.columns):
            output_dict['dist_mtrx'] = get_distance_matrix(df)
            print "There are {0} station locations in the distance matrix".format(len(output_dict['dist_mtrx'].index))
        else:
            raise GenericException("Missing required input columns for distance matrix calc: {}".format(dm_mandatory_columns - set(df.columns)))

    return output_dict
