def REI(detections, deployments):

    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_detection_columns = set(['datecollected', 'fieldnumber', 'scientificname', 'station'])
    mandatory_deployment_columns = set(['station_name', 'deploy_date', 'recovery_date', 'last_download'])

    if mandatory_detection_columns.issubset(detections.columns) and mandatory_deployment_columns.issubset(deployments.columns):

        deployments = deployments.copy(deep=True)
        deployments['recovery_notes'] = deployments.recovery_date.str.extract('([A-Za-z\//:]+)', expand=False)
        deployments.recovery_date = deployments.recovery_date.str.extract('(\d+-\d+-\d+)', expand=False)
        deployments.loc[deployments.recovery_date.isnull(), 'recovery_date'] = deployments.last_download
        deployments = deployments[(deployments.last_download != '-') & (deployments.recovery_date != '-')]

        deployments.deploy_date = pd.to_datetime(deployments.deploy_date)
        deployments.recovery_date = pd.to_datetime(deployments.recovery_date)
        deployments.last_download = pd.to_datetime(deployments.last_download)

        deployments['days_deployed'] = deployments[['last_download', 'recovery_date']].max(axis=1) - deployments.deploy_date

        detections = detections[detections.station.isin(deployments.station_name)]

        days_active = deployments.groupby('station_name').agg({'days_deployed':'sum'}).reset_index()
        days_active.set_index('station_name', inplace=True)

        array_unique_tags = len(detections.fieldnumber.unique())
        array_unique_species = len(detections.scientificname.unique())
        days_with_detections = len(pd.to_datetime(detections.datecollected).dt.date.unique())
        station_reis = pd.DataFrame(columns=['station','rei'])

        for name, data in detections.groupby('station'):
            receiver_unique_tags = len(data.fieldnumber.unique())
            receiver_unique_species = len(data.scientificname.unique())
            receiver_days_with_detections = len(pd.to_datetime(data.datecollected).dt.date.unique())


            if name in days_active.index:
                receiver_days_active = days_active.loc[name].days_deployed.days
                if receiver_days_active > 0:
                    rei = ((receiver_unique_tags/array_unique_tags) * (receiver_unique_species/array_unique_species))/(days_with_detections/receiver_days_with_detections)/receiver_days_active
                    station_reis = station_reis.append({'station':name, 'rei':rei, 'latitude':data.latitude.mean(), 'longitude':data.longitude.mean()}, ignore_index=True)
            else:
                print("No valid deployment record for "+name)




        station_reis.rei = station_reis.rei/ station_reis.rei.sum()
        del deployments
        return station_reis
    else:
        raise GenericException("Missing required input columns: {}".format(mandatory_columns - set(detections.columns)))
