from resonate.filter_detections import get_distance_matrix
from datetime import datetime, timedelta
import pandas as pd

def velocity_filter(detections, max_vel=10):
    pd.options.mode.chained_assignment = None
    dm = get_distance_matrix(detections)

    lead_lag_df = pd.DataFrame()

    for index, group in detections.sort_values(['datecollected']).groupby(['catalognumber']):
        group['lag_station'] = group.station.shift(1).fillna(group.station)
        group['lead_station'] = group.station.shift(-1).fillna(group.station)

        group.datecollected = pd.to_datetime(group.datecollected)
        group['lag_time_diff'] = group.datecollected.diff().fillna(timedelta(seconds=1))
        group['lead_time_diff'] = group.lag_time_diff.shift(-1).fillna(timedelta(seconds=1))

        lead_lag_df = lead_lag_df.append(group)

    del detections

    vel_df = pd.DataFrame()
    for index, group in lead_lag_df.groupby(['station', 'lag_station', 'lead_station']):
        stn = group.station.unique()[0]
        lag_stn = group.lag_station.unique()[0]
        lead_stn = group.lead_station.unique()[0]

        lag_distance = dm.loc[stn, lag_stn].m
        lead_distance = dm.loc[stn, lead_stn].m

        group['lag_distance_m'] = lag_distance
        group['lead_distance_m'] = lead_distance
        vel_df = vel_df.append(group)

    del lead_lag_df

    vel_df['lag_velocity'] = vel_df.lag_distance_m/vel_df.lag_time_diff.dt.total_seconds()
    vel_df['lead_velocity'] = vel_df.lead_distance_m/vel_df.lead_time_diff.dt.total_seconds()
    vel_df.sort_index(inplace=True)
    filtered_detections = dict()
    filtered_detections['filtered'] = vel_df[(vel_df.lag_velocity <= max_vel) & (vel_df.lead_velocity <= max_vel)].reset_index(drop=True)
    filtered_detections['suspect'] = vel_df[(vel_df.lag_velocity > max_vel) | (vel_df.lead_velocity > max_vel)].reset_index(drop=True)
    return filtered_detections
