import datetime

import numpy as np
import pandas as pd
from resonate.library.exceptions import GenericException


def REI(detections, deployments):
    '''
    Calculates a returns a list of each station and the REI (defined here):

    :param detections: a pandas DataFrame of detections
    :param deployments: a pandas DataFrame of station deployment histories

    :return: a pandas DataFrame of station, REI, latitude, and longitude
    '''

    # Check for proper dataframe and the correct columns
    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_detection_columns = set(
        ['datecollected', 'fieldnumber', 'scientificname', 'station'])
    mandatory_deployment_columns = set(
        ['station_name', 'deploy_date', 'recovery_date', 'last_download'])

    if mandatory_detection_columns.issubset(detections.columns) and \
            mandatory_deployment_columns.issubset(deployments.columns):

        # Copy and change the deployments to create dates in the 3 mandatory
        # date columns
        deployments = deployments.copy(deep=True)
        detections = detections.copy(deep=True)
        if deployments.recovery_date.dtype != np.dtype('<M8[ns]'):
            deployments['recovery_notes'] = deployments.recovery_date.str.extract(
                '([A-Za-z\//:]+)', expand=False)
            deployments.recovery_date = deployments.recovery_date.str.extract(
                '(\d+-\d+-\d+)', expand=False)
            deployments = deployments.replace('-', np.nan)
        deployments.loc[deployments.recovery_date.isnull(
        ), 'recovery_date'] = deployments.last_download

        deployments = deployments[~deployments.recovery_date.isnull()]
        # Cast the date columns to a datetime
        deployments.deploy_date = pd.to_datetime(deployments.deploy_date)
        deployments.recovery_date = pd.to_datetime(deployments.recovery_date)
        deployments.last_download = pd.to_datetime(deployments.last_download)

        # Calculate each receivers total days deployed
        deployments['days_deployed'] = deployments.recovery_date - \
            deployments.deploy_date

        days_active = deployments.groupby('station_name').agg(
            {'days_deployed': 'sum'}).reset_index()
        days_active.set_index('station_name', inplace=True)
        # Exclude all detections that are not registered with receivers in the
        # deployments
        detections = detections[detections.station.isin(
            deployments.station_name)]

        # Calculate array counts and initialize the dataframe
        array_unique_tags = len(detections.fieldnumber.unique())
        array_unique_species = len(detections.scientificname.unique())
        days_with_detections = len(pd.to_datetime(
            detections.datecollected).dt.date.unique())
        array_days_active = (max(deployments.last_download.max(
        ), deployments.recovery_date.max()) - min(deployments.deploy_date)).days

        station_reis = pd.DataFrame(columns=['station', 'rei'])

        # Loop through each station in the detections and Calculate REI for
        #  oeach station
        detections.datecollected = pd.to_datetime(
            detections.datecollected).dt.date

        # Loop through each station in the detections and Calculate REI for
        #  oeach station
        for name, data in detections.groupby('station'):
            receiver_unique_tags = len(data.fieldnumber.unique())
            receiver_unique_species = len(data.scientificname.unique())
            receiver_days_with_detections = len(
                pd.to_datetime(data.datecollected).dt.date.unique())

            if name in days_active.index:
                receiver_days_active = days_active.loc[name].days_deployed.days
                if receiver_days_active > 0:
                    rei = (receiver_unique_tags / array_unique_tags) * \
                        (receiver_unique_species / array_unique_species) * \
                        (receiver_days_with_detections / days_with_detections) * \
                        (array_days_active / receiver_days_active)
                    station_reis = station_reis.append({
                        'station': name,
                        'rei': rei,
                        'latitude': data.latitude.mean(),
                        'longitude': data.longitude.mean()},
                        ignore_index=True)
            else:
                print("No valid deployment record for " + name)

        # Normalize REIs to value from 0 to 1
        station_reis.rei = station_reis.rei / station_reis.rei.sum()

        # Cleanup and return the station REI's
        del deployments
        return station_reis
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))
