import pandas as pd


def cohort(compressed_df, interval_time=60):
    """
    Creates a dataframe of cohorts using a compressed detection file

    :param compressed_df: compressed dataframe
    :param interval_time: cohort detection time interval (in minutes)
    :return: cohort dataframe with the following columns

        * anml_1
        * anml_1_seq
        * station
        * anml_2
        * anml_2_seq
        * anml_2_arrive
        * anml_2_depart
        * anml_2_startunqdetecid
        * anml_2_endunqdetecid
        * anml_2_detcount

    """

    # Convert input int interval_time into a timedelta object
    interval_time = pd.to_timedelta(interval_time, unit='m')

    # Sort input compressed data file
    cmps = compressed_df.sort_values(['catalognumber', 'seq_num'])

    # Loop through rows in the compressed data file and choose
    # cohorts if the times are within range
    seen = []
    final_set = []

    for idx1, item1 in cmps.iterrows():
        match = cmps[
            (cmps.station == item1.station) &
            (cmps.catalognumber != item1.catalognumber) &
            (~cmps.index.to_series().apply(lambda x: (x, idx1)).isin(seen)) &
            ((cmps.startdate > item1.startdate - interval_time) &
                (cmps.startdate < item1.enddate + interval_time) |
                (cmps.enddate > item1.startdate - interval_time) &
                (cmps.enddate < item1.enddate + interval_time))]

        if not match.empty:
            match.insert(0, 'anml_1', item1.catalognumber)
            match.insert(1, 'anml_1_seq', item1.seq_num)
            final_set.extend(match[['anml_1', 'anml_1_seq', 'station',
                                    'catalognumber', 'seq_num', 'startdate',
                                    'enddate', 'startunqdetecid',
                                    'endunqdetecid', 'total_count'
                                    ]].values.tolist())
            seen.extend([(idx1, i) for i in match.index.tolist()])

    output_df = pd.DataFrame(final_set)
    output_df.columns = ['anml_1',
                         'anml_1_seq',
                         'station',
                         'anml_2',
                         'anml_2_seq',
                         'anml_2_arrive',
                         'anml_2_depart',
                         'anml_2_startunqdetecid',
                         'anml_2_endunqdetecid',
                         'anml_2_detcount']
    return output_df
