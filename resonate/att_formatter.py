import pandas as pd


def create_att_dictionary_format(dets_file=None, tags_file=None, deployment_file=None, preprocessed=None):
    """Creates a dictionary with dataframes containing detections, tag metadata, and station metadata.
    Heavily inspired by VTrack's ATT format. Either the 3 file args must not be none or the preprocessed
    arg must not be none. If all are not none, preprocessed will be used.

    Args:
        dets_file (str, optional): path to the OTN detection extract file. Defaults to None.
        tags_file (str, optional): path to the OTN tagging metadata excel file. Defaults to None.
        deployment_file (str, optional): path to the OTN deployment metadata excel file. Defaults to None.
        preprocessed (dict, optional): dictionary containing ALL THREE dataframes normally created by 
            the file args. Dict keys are 'dets', 'tags', 'deploys'. Defaults to None.

    Returns:
        dict: A dictionary containing 3 dataframe for detections, tagging metadata, and station metadata
    """
    att = {}
    # Make sure preprocessed is there and that everything is in it
    if preprocessed is not None and all(x in preprocessed for x in ['dets', 'tags', 'deploys']): 
        dets = preprocessed['dets']
        tags = preprocessed['tags']
        deploys = preprocessed['deploys']
    # Check if all file args are there
    elif all(x is not None for x in [dets_file, tags_file, deployment_file]):
        dets = pd.read_csv(dets_file)
        tags = setup_tag_sheet(tags_file)
        deploys = setup_deployment_sheet(deployment_file)
    else:
        raise RuntimeError("Arguments incorrect, please insure that all file args are there or the preprocessed dict is there.")

    # clean up station and receiver so they don't show (lost/found)
    dets['station_name'] = dets['station'].str.extract(
        '([A-Za-z0-9]*)(\\(lost/found\\))?')[0]
    dets['receiver'] = dets['receiver'].str.extract(
        '([0-9]*)(\\(lost/found\\))?')[0]
    dets.rename({'tagname': 'transmitter_id'}, inplace=True, axis=1)
    dets_joined_tags = dets.merge(
        tags, how='left', left_on='transmitter_id', right_on='transmitter_id')  # Add tag data to dets

    dets_joined_tags.rename({
        'catalognumber': 'tag_id',
        'transmitter_id': 'transmitter',
        'collectioncode': 'tag_project',
    }, inplace=True, axis=1)

    # We don't track tag_status or bio, set to none
    dets_joined_tags['tag_status'] = None
    dets_joined_tags['bio'] = None

    # Select all required columns and drop dupes
    att['tag_metadata'] = dets_joined_tags[
        ['tag_id', 'transmitter', 'common_name', 'sci_name', 'tag_project', 'release_latitude',
         'release_longitude', 'release_date', 'sex', 'tag_life', 'tag_status', 'bio']
    ].drop_duplicates()

    att['tag_metadata'] = reindex_df(att['tag_metadata'])

    dets_joined_full = dets_joined_tags.merge(
        deploys, how="left", left_on='station_name', right_on='station_name')  # Add station data to dets
    dets_joined_full['installation'] = None
    dets_joined_full['receiver_status'] = None
    # Create full receiver, if it's not already complete
    if '-' not in dets_joined_full['ins_model_no'].all():
        dets_joined_full['receiver'] = dets_joined_full['ins_model_no'] + \
            '-' + dets_joined_full['receiver']
    att['station_information'] = dets_joined_full[
        ['station_name', 'receiver', 'installation', 'receiver_project',
         'deploy_date_time', 'recover_date_time', 'deploy_lat', 'deploy_long', 'receiver_status']]

    att['station_information'] = att['station_information'].drop_duplicates(
    ).sort_values('station_name')
    att['station_information'] = reindex_df(att['station_information'])

    att['tag_detections'] = dets_joined_full[
        ['datecollected', 'transmitter', 'station_name', 'receiver',
         'latitude', 'longitude', 'sensorvalue', 'sensorunit']]

    return att


def setup_tag_sheet(path):
    """Imports the tag sheet and extracts the parts that are needed for the ATT like dict.

    Args:
        path (str): Path to the tagging sheet

    Returns:
        pd.DataFrame: Dataframe needed by 'create_att_dictionary_format'
    """
    tags = pd.read_excel(path, sheet_name=1, header=4)
    tags['transmitter_id'] = tags['TAG_CODE_SPACE'].astype(
        str) + '-' + tags['TAG_ID_CODE'].astype(str)
    tags['tag_life'] = tags['EST_TAG_LIFE'].apply(get_days_from_string)

    tag_cols = ['ANIMAL_ID   (floy tag ID, pit tag code, etc.)', 'UTC_RELEASE_DATE_TIME',
                'SEX',
                'RELEASE_LATITUDE',
                'RELEASE_LONGITUDE',
                'UTC_RELEASE_DATE_TIME',
                'COMMON_NAME_E',
                'SCIENTIFIC_NAME',
                'transmitter_id',
                'tag_life']

    tag_renames = ['animal_id',
                   'time',
                   'sex',
                   'release_latitude',
                   'release_longitude',
                   'release_date',
                   'common_name',
                   'sci_name',
                   'transmitter_id',
                   'tag_life']

    return subset_rename_df(tags, tag_cols, tag_renames)


def setup_deployment_sheet(path, pad_station=True):
    """Imports the deployment sheet and extracts the parts that are needed for the ATT like dict.

    Args:
        path (str): Path to the deployment sheet
        pad_station (bool, optional): If the station number should be padded to be a 3 digit number (34 -> 034). Defaults to True.

    Returns:
        pd.DataFrame: Dataframe needed by 'create_att_dictionary_format'
    """
    deploys = pd.read_excel(path)
    deploy_cols = ['DEPLOY_LAT',
                   'DEPLOY_LONG',
                   'INS_MODEL_NO',
                   'DEPLOY_DATE_TIME   (yyyy-mm-ddThh:mm:ss)',
                   'RECOVER_DATE_TIME (yyyy-mm-ddThh:mm:ss)',
                   'OTN_ARRAY',
                   'station_name']

    deploy_renames = ['deploy_lat',
                      'deploy_long',
                      'ins_model_no',
                      'deploy_date_time',
                      'recover_date_time',
                      'receiver_project',
                      'station_name']

    if pad_station:
        deploys['STATION_NO'] = deploys['STATION_NO'].apply(pad_number)
    deploys['station_name'] = deploys['OTN_ARRAY'].astype(str) + deploys['STATION_NO'].astype(str)
    return subset_rename_df(deploys, deploy_cols, deploy_renames)


def subset_rename_df(df, subset, names):
    """Subsets a dataframe then renamed all the columns of the subset.

    Args:
        df (pd.DataFrame): A Pandas DataFrame
        subset (list): A list of columns to select
        names (list): A list of renamed columns, in the same order and 'subset'

    Raises:
        RuntimeError: Raised if the length of 'subset' and 'names' aren't the same

    Returns:
        pd.DataFrame: New dataframe containing the columns from 'subset', renamed to the names in 'names'
    """
    if (len(subset) != len(names)):
        raise RuntimeError("'subset' and 'names' must be the same length. %s != %s" % (
            len(subset), len(names)))
    new_df = df[subset]
    new_df.columns = names
    return new_df


def get_days_from_string(string):
    """Attempts to convert written text to a time delta then return the amount of days

    Args:
        string (str): The timedelta in text form

    Raises:
        Exception: if casting to int and 'to_timedelta' doesn't work.

    Returns:
        [type]: [description]
    """
    try:
        return int(string)
    except ValueError:
        pass  # Attempting to use to_timedelta
    try:
        return pd.to_timedelta(string).days
    except KeyError:
        raise Exception("Please change the estimated tag life to days.")


def pad_number(num, size=3):
    """Pads a number with zeros in the front until 'size' is reached. 
    Does not shorten string to 'size.

    Args:
        num (int): The number to be padded
        size (int, optional): The length of the number after padding. Defaults to 3.

    Returns:
        [type]: [description]
    """
    num = str(num)
    while len(num) < size:
        num = f"0{num}"
    return num


def reindex_df(df):
    """Sets the index of a dataframe to 0 to (size - 1)

    Args:
        df (pd.DataFrame): A dataframe

    Returns:
        pd.DataFrame: The dataframe that was passed in with a 0 to N-1 index.
    """
    df.index = range(0, len(df))
    return df
