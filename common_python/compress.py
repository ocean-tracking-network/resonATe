# -*- coding: utf-8 -*-

import ConfigParser
import argparse
import os
import sys

from library.verifications import FileVersionID, TableExists, Filename, TableCount
from library import compress_detections

import load_detections

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

import MessageDB as mdb
msgs = mdb.MessageDB()

import table_maintenance as tm


def CompressDetections(detection_file,
                       reload_detections=False,
                       data_directory='/home/sandbox/RStudio/data/'):
    '''
    Creates mv_anm_compressed table from detection file
    :param detection_file: detection file
    :param reload_detections: whether or not to reload the detection file
    :param data_directory: directory where the data files are stored (absolute)
    '''

    # Verify file name
    if not Filename( detection_file ):
        print msgs.get_message(index=70,params=[detection_file])
        return False

    # Get table name from detection file name, check for input version id too
    version_id = FileVersionID( detection_file )

    if version_id:
        detection_tbl = detection_file.replace('.csv', '').lower()
    else:
        detection_tbl = detection_file.lower().replace('.csv','').replace(' ', '_') + '_v00'
        version_id = '00'

    # Determine if table already exists in the database
    table_exists = TableExists( detection_tbl )

    # If reload is specified, replace table with new csv file
    if (table_exists and reload_detections) or not table_exists:
        # Using loadDetections module
        detections_loaded = load_detections.loadDetections(detection_file=detection_file,
                                       version_id=version_id,
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval=60,
                                       data_directory= data_directory)
        if detections_loaded == -1:
            return -1

    # Table row count
    table_row_count = TableCount(  detection_tbl )

    # Indicate to the user that the script will use the already loaded data
    print msgs.get_message(index=71, params=[detection_tbl, table_row_count])

    mv_anm_det_exists = TableExists('mv_anm_detections')

    database = tm.table_maintenance(reqcode='reqconn')

    if mv_anm_det_exists:
        database.table_maintenance(reqcode='reqdropcscd',
                             tablename='mv_anm_detections')

    # rename detection table to mv_anm_detections
    database.table_maintenance(reqcode='reqrename',
                               tablename=[detection_tbl, 'mv_anm_detections'])

    # Compress new detection csv table
    compress_detections.compress_detections()
    # get table count
    compressed_count = TableCount( 'mv_anm_compressed' )

    # rename detection table back from mv_anm_detections
    database.table_maintenance(reqcode='reqrename',
                               tablename=['mv_anm_detections', detection_tbl])

    # Output message
    print msgs.get_message(index=72, params=[detection_tbl, compressed_count])

    # Close connections
    database.table_maintenance(reqcode='reqdisconn')