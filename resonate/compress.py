# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from library.exceptions import GenericException

def compress_detections(detections):

    '''
    Creates compressed dataframe from detection dataframe

    :param detections: detection dataframe
    '''

    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_columns = set(['datecollected', 'catalognumber', 'unqdetecid'])

    if mandatory_columns.issubset(detections.columns):

        # Get unique list of animals (not tags), set indices to respect animal and date of detections
        anm_list = detections['catalognumber'].unique()
		# Can't guarantee they've sorted by catalognumber in the input file.
        detections.sort_values(['catalognumber', 'datecollected'], inplace=True)

        # Set up empty data structures and the animal-based groupby object
        detections['seq_num'] = np.nan
        anm_group = detections.groupby('catalognumber')
        out_df = pd.DataFrame()

        # for each animal's detections ordered by time, when station changes, seqnum is incremented.
        for catalognum in anm_list:
            a = anm_group.get_group(catalognum).copy(deep=True)
            # Some say I'm too cautious. Shift logic requires this sort to be true, though.
            a.sort_values(['datecollected', 'station'], inplace=True)

            a['seq_num'] = (a.station.shift(1) != a.station).astype(int).cumsum()
            out_df=out_df.append(a)

        stat_df = out_df.groupby(['catalognumber','seq_num']).agg({  'datecollected':['min', 'max'],
                                                                    'unqdetecid':['first','last'],
                                                                    'seq_num': 'count'})

        # Flatten the multi-index into named columns and cast dates to date objects
        stat_df.columns = ['_'.join(col).strip() for col in stat_df.columns.values]
        stat_df.datecollected_max = pd.to_datetime(stat_df.datecollected_max)
        stat_df.datecollected_min = pd.to_datetime(stat_df.datecollected_min)

        # Calculate average time between detections
		# If it's a single detection, will be 0/1
        stat_df['avg_time_between_det'] = (stat_df['datecollected_max'] - stat_df['datecollected_min']) / np.maximum(1, stat_df['seq_num_count']-1)

        stat_df.rename(columns={'seq_num_count': 'total_count', 'datecollected_max': 'enddate',
								'datecollected_min':'startdate', 'unqdetecid_first': 'startunqdetecid',
								'unqdetecid_last':'endunqdetecid'}, inplace=True)
        # Reduce indexes to regular columns for joining against station number.
        stat_df.reset_index(inplace=True)

        # Join stations to result. Could add lat/lon here as well.
        out_df = out_df[['catalognumber', 'station', 'seq_num']].drop_duplicates().merge(stat_df, on=['catalognumber', 'seq_num'])

        return out_df
    else:
        raise GenericException("Missing required input columns: {}".format(mandatory_columns - set(detections.columns)))