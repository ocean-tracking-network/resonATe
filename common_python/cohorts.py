# -*- coding: utf-8 -*-

import ConfigParser
import argparse
import os
import sys

from library.pg_connection import createConnection
from library.verifications import FileCount

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

import MessageDB as mdb
msgs = mdb.MessageDB()

def CohortRecords(interval_time=60,
                  data_directory='/home/sandbox/RStudio/data/'):
    '''
    Function to determine cohorts from a compresseed detection file
    :param input_file: compressed detection file
    :param interval_time: The time used to determine whether two or more animals are cohorts
    :return: return result of cohort detections
    '''
    # Variable assignment
    interval_time = interval_time
    data_directory = data_directory

    # Create cursor object
    conn, cur = createConnection()

    # SQL used to create cohort export
    cohort_sql = """
    COPY (
        select fst.catalognumber,fst.seq_num, snd.* from (select * from mv_anm_compressed) fst
        join (select * from mv_anm_compressed) snd
        on  fst.catalognumber < snd.catalognumber
        and fst.station = snd.station
        and (snd.startdate between (fst.startdate - interval'{0} minutes')
                                     and (fst.enddate + interval'{0} minutes')
            or snd.enddate between (fst.startdate - interval'{0} minutes')
                                     and (fst.enddate + interval'{0} minutes'))
        order by 1,2,3,4
    ) TO STDOUT WITH CSV HEADER QUOTE AS '"';
    """.format(interval_time)

    # Path name & File handler creation
    file_name = 'cohort_{0}min.csv'.format(interval_time)
    file_path = os.path.join(data_directory, file_name)
    fh = open(file_path, 'wb')

    # Export Data
    cur.copy_expert(cohort_sql, fh)
    fh.close()

    # Close the database connections
    cur.close()
    conn.close()

    # Count the number of records in the file
    file_count = FileCount(file_path, header=True)

    # Print final message to console
    print msgs.get_message(index=60,params=[file_name, file_count])