from resonate.filter_detections import get_distance_matrix
from datetime import datetime, timedelta
import pandas as pd

def distance_filter(detections, max_dist=100000):
    pd.options.mode.chained_assignment = None
    dm = get_distance_matrix(detections)

    lead_lag_stn_df = pd.DataFrame()

    for index, group in detections.sort_values(['datecollected']).groupby(['catalognumber']):
        group['lag_station'] = group.station.shift(1).fillna(group.station)
        group['lead_station'] = group.station.shift(-1).fillna(group.station)
        lead_lag_stn_df = lead_lag_stn_df.append(group)

    del detections

    distance_df = pd.DataFrame()

    for index, group in lead_lag_stn_df.groupby(['station', 'lag_station', 'lead_station']):
        stn = group.station.unique()[0]
        lag_stn = group.lag_station.unique()[0]
        lead_stn = group.lead_station.unique()[0]
        lag_distance = dm.loc[stn, lag_stn].m
        lead_distance = dm.loc[stn, lead_stn].m
        group['lag_distance_km'] = lag_distance
        group['lead_distance_km'] = lead_distance
        distance_df = distance_df.append(group)

    del lead_lag_stn_df
    distance_df.sort_index(inplace=True)

    filtered_detections = dict()
    filtered_detections['filtered'] = distance_df[(distance_df.lag_distance_km <= max_dist) & (distance_df.lead_distance_km <= max_dist)].reset_index(drop=True)
    filtered_detections['suspect'] = distance_df[(distance_df.lag_distance_km > max_dist) | (distance_df.lead_distance_km > max_dist)].reset_index(drop=True)
    return filtered_detections
