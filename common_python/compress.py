# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from library.verifications import GenericException

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
        anm_df = detections['catalognumber'].unique()
        detections.set_index(['catalognumber', 'datecollected'])

        # Set up empty data structures and the animal-based groupby object
        detections['seqnum'] = np.nan
        anm_group = detections.groupby('catalognumber')
        out_df = pd.DataFrame()

        # for each animal's detections ordered by time, when station changes, seqnum is incremented.
        for catalognum in anm_df:
            a = anm_group.get_group(catalognum)
            a.reset_index('datecollected')
            a['seqnum'] = (a.station.shift(1) != a.station).astype(int).cumsum()
            out_df=out_df.append(a)

        stat_df = out_df.groupby(['catalognumber','seqnum']).agg({  'datecollected':['min', 'max'],
                                                                    'unqdetecid':['min','max'],
                                                                    'seqnum': 'count'})

        # Flatten the multi-index into named columns and cast dates to date objects
        stat_df.columns = ['_'.join(col).strip() for col in stat_df.columns.values]
        stat_df.datecollected_max = pd.to_datetime(stat_df.datecollected_max)
        stat_df.datecollected_min = pd.to_datetime(stat_df.datecollected_min)

        # Calculate average time between detections
        stat_df['avg_time_between_det'] = (stat_df['datecollected_max'] - stat_df['datecollected_min']) / stat_df['seqnum_count']

        # Reduce indexes to regular columns for joining against station number.
        stat_df.reset_index(inplace=True)

        # Join stations to result. Could add lat/lon here as well.
        out_df = out_df[['catalognumber', 'station', 'seqnum']].drop_duplicates().merge(stat_df, on=['catalognumber', 'seqnum'])

        return out_df
    else:
        raise GenericException("Missing required input columns: {}".format(mandatory_columns - set(detections.columns)))
