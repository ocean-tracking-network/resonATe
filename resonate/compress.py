# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from resonate.library.exceptions import GenericException

def compress_detections(detections: pd.DataFrame, timefilter=3600, keep_columns=False, keep_columns_agg='first',
                        col_catalognumber:str='catalogNumber', col_station:str='station', col_latitude:str='decimalLatitude',
                        col_longitude:str='decimalLongitude', col_datecollected:str='dateCollectedUTC', col_unique_id:str='unqDetecID',
                        **kwargs):
    """Creates compressed dataframe from detection dataframe

    Args:
        detections (pd.DataFrame): detection dataframe
        timefilter (int, optional): A maximum amount of time in seconds that can pass before
        a new detction event is started. Defaults to 3600.
        keep_columns (bool, optional): Keep the extra columns from the detection file not required to create 
        the compressed dataframe. Defaults to False.
        keep_columns_agg (str|func, optional): If keep_columns is true, defines how to handle aggregation 
        of duplicate rows. Supports 'first', 'last', or a function. Defaults to 'first'.

    Raises:
        GenericException: Triggered if detections is not a dataframe.
        GenericException: Triggered if detections file is missing required columns

    Returns:
        pd.DataFrame: A compressed dataframe of detection events.
    """

    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_columns = set(
        [col_datecollected, col_catalognumber, col_unique_id, col_latitude, col_longitude])

    if mandatory_columns.issubset(detections.columns):
        stations = detections.groupby(col_station, dropna=False).agg(
            'mean', 1)[[col_latitude, col_longitude]].reset_index()

        # Get unique list of animals (not tags), set indices to respect animal and date of detections
        anm_list = detections[col_catalognumber].unique()
        # Can't guarantee they've sorted by catalognumber in the input file.
        detections.sort_values(
            [col_catalognumber, col_datecollected], inplace=True)

        # Set up empty data structures and the animal-based groupby object
        detections['seq_num'] = np.nan
        anm_group = detections.groupby(col_catalognumber, dropna=False)
        out_df = pd.DataFrame()

        # for each animal's detections ordered by time, when station changes, seqnum is incremented.
        for catalognum in anm_list:
            a = anm_group.get_group(catalognum).copy(deep=True)
            # Some say I'm too cautious. Shift logic requires this sort to be true, though.
            a.sort_values([col_datecollected, col_station], inplace=True)
            a[col_datecollected] = pd.to_datetime(a[col_datecollected])
            a['seq_num'] = ((a[col_station].shift(1) != a[col_station]) | (
                a[col_datecollected].diff().dt.total_seconds() > timefilter)).astype(int).cumsum()
            out_df = pd.concat([out_df, a])

        stat_df = out_df.groupby([col_catalognumber, 'seq_num'], dropna=False).agg({col_datecollected: ['min', 'max'],
                                                                    col_unique_id: ['first', 'last'],
                                                                    'seq_num': 'count'})

        # Flatten the multi-index into named columns and cast dates to date objects
        stat_df.columns = ['_'.join(col).strip()
                           for col in stat_df.columns.values]

        stat_df[f'{col_datecollected}_max'] = pd.to_datetime(stat_df[f'{col_datecollected}_max'])
        stat_df[f'{col_datecollected}_min'] = pd.to_datetime(stat_df[f'{col_datecollected}_min'])

        # Calculate average time between detections
        # If it's a single detection, will be 0/1
        stat_df['avg_time_between_det'] = (
            stat_df[f'{col_datecollected}_max'] - stat_df[f'{col_datecollected}_min']) / np.maximum(1, stat_df['seq_num_count'] - 1)

        stat_df.rename(columns={'seq_num_count': 'total_count', f'{col_datecollected}_max': 'enddate',
                                f'{col_datecollected}_min': 'startdate', f'{col_unique_id}_first': 'startunqdetecid',
                                f'{col_unique_id}_last': 'endunqdetecid'}, inplace=True)
        # Reduce indexes to regular columns for joining against station number.
        stat_df.reset_index(inplace=True)

        if keep_columns:
            # Group and aggregate out_df to mimic drop_duplicates
            agg_df = out_df.groupby([col_catalognumber, col_station, 'seq_num']).agg(keep_columns_agg).reset_index()
            # Rename lat and long columns in detections
            if col_latitude in agg_df.columns:
                print(f"Found column named '{col_latitude}' in detection dataframe, renaming to 'detection_latitude'.")
                agg_df.rename(columns={col_latitude: 'detection_latitude'}, inplace=True)
            if col_longitude in agg_df.columns:
                print(f"Found column named '{col_longitude}' in detection dataframe, renaming to 'detection_longitude'.")
                agg_df.rename(columns={col_longitude: 'detection_longitude'}, inplace=True)
            out_df = agg_df.merge(stat_df, on=[col_catalognumber, 'seq_num'])
        else:
            # Join stations to result. Could add lat/lon here as well.
            out_df = out_df[[col_catalognumber, col_station, 'seq_num']].drop_duplicates(
            ).merge(stat_df, on=[col_catalognumber, 'seq_num'])

        out_df = out_df.merge(stations, on=col_station)

        return out_df
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))
