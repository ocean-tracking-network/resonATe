
import pandas as pd
import numpy as np
from geopy.distance import vincenty

shore = (44.481269, -63.534769)
detections = pd.read_csv('hfx_qualified_detections_2014.csv')
stations = pd.read_csv('stations_receivers.csv')
depths = pd.read_csv('hfx_2016-09-21_metadata_deployment.csv')
releases = pd.read_csv('nsbs_matched_detections_2014.csv')
releases = releases[releases.receiver == 'release'][['latitude', 'longitude']].reset_index(drop=True)

depths['station'] = depths.OTN_ARRAY + depths.STATION_NO
depths = depths[['station', 'BOTTOM_DEPTH']].set_index('station')
depths.columns = ['depth']
depths = depths.groupby('station').mean()


# In[2]:


stations.deploy_date = pd.to_datetime(stations.deploy_date)
stations = stations[(stations.deploy_date < '2015')
                    & (stations.recovery_date > '2014')
                    & (~stations.recovery_date.str.contains('|'.join(['lost', 'off', 'caught','failed', 'moved'])))
                   & (~stations.station_name.str.contains('lost'))]

stations.loc[stations.deploy_date < '2014', 'deploy_date'] = '2014-01-01'
stations.loc[stations.recovery_date > '2014-12-31', 'recovery_date'] = '2015-01-01'
stations.deploy_date = pd.to_datetime(stations.deploy_date)
stations.recovery_date = pd.to_datetime(stations.recovery_date)

stations['days_deployed'] = (stations.recovery_date - stations.deploy_date)
stations = stations[['station_name', 'stn_lat', 'stn_long','days_deployed', 'off_set']].drop_duplicates().reset_index(drop=True)
stations.set_index('station_name', inplace=True)


# In[3]:


detections['num_of_dets'] = 1
dets_counts_df = detections[['station', 'num_of_dets']].groupby('station', as_index=False).agg('count')
dets_counts_df.set_index('station', inplace=True)


# In[4]:


unique_transmitters_per_station = detections[['station', 'fieldnumber']].groupby(['station']).fieldnumber.nunique()


# In[5]:


stats = stations.join(dets_counts_df).join(unique_transmitters_per_station).join(depths).dropna()
stats.columns = ['latitude', 'longitude','days_deployed', 'num_of_dets', 'num_of_transmitters',  'off_set', 'depth']


# In[6]:


stats['detections_index'] = stats.num_of_dets/stats.days_deployed.dt.days
stats['transmitters_index'] = stats.num_of_transmitters/stats.days_deployed.dt.days
stats['receiver_depth'] = stats.depth - stats.off_set
stats['releases_within_10_km'] = 0
stats['releases_within_50_km'] = 0
stats['releases_within_100_km'] = 0


# In[7]:


for s_index , stn in stats.iterrows():
    station_point = (stn.latitude, stn.longitude)
    distance = vincenty(station_point, shore)
    stats.loc[s_index, 'offshore_distance_km'] = distance.km
    for r_index, rel in releases.iterrows():
        release_point = (rel.latitude, rel.longitude)
        release_distance = vincenty(station_point, release_point)
        if release_distance.km <= 10:
            stats.loc[s_index, 'releases_within_10_km'] += 1
        if release_distance.km <= 50:
            stats.loc[s_index, 'releases_within_50_km'] += 1
        if release_distance.km <= 100:
            stats.loc[s_index, 'releases_within_100_km'] += 1


# In[8]:


line_stats = {
    'data':stats,
    'detections_mean': stats.detections_index.mean(),
    'detections_std_dev': np.std(stats.detections_index),
    'detections_range': stats.detections_index.max() - stats.detections_index.min(),
    'tranmitters_mean': stats.transmitters_index.mean(),
    'transmitters_std_dev': np.std(stats.transmitters_index),
    'transmitters_range': stats.transmitters_index.max() - stats.transmitters_index.min()
}
