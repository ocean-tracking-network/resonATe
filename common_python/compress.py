# -*- coding: utf-8 -*-

import ConfigParser
import argparse
import os
import sys

from library.verifications import FileVersionID, TableExists, Filename, TableCount, FileExists
from library import compress_detections
from library.copy_from_postgresql import ExportTable 

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
        # Error: {detection_file} variable supplied either has invalid characters or does not contain a csv file extension
        print msgs.get_message(index=70,params=[detection_file])
        return False
    
    # Test to see file exists
    if not FileExists(os.path.join(data_directory, detection_file)):
        # File {detection_file} does not exist
        print msgs.get_message(index=19,params=[detection_file])
        return False

    # Get table name from detection file name, check for input version id too
    version_id = FileVersionID( detection_file )

    if version_id:
        detection_tbl = detection_file.replace('.csv', '').lower()
        # Create export file name 
        export_compr_file = detection_file.lower().replace('_v'+version_id+'.csv', '_compressed_detections_v'+version_id+'.csv' )
    else:
        detection_tbl = detection_file.lower().replace('.csv','').replace(' ', '_') + '_v00'
        version_id = '00'
        # Create export file name 
        export_compr_file = detection_file.lower().replace('.csv', '_compressed_detections_v00.csv')

    # Determine if the export file exists and return an error if it does
    export_exists = FileExists(os.path.join(data_directory, export_compr_file))
    
    if export_exists:
        # Output File {export_compr_file} already existed. Please rename or delete the file and rerun process.
        print msgs.get_message(index=20, params=[export_compr_file])
        return False
    
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
                                       detection_radius=0,
                                       data_directory= data_directory)
        if detections_loaded == -1:
            return -1

    # Table row count
    table_row_count = TableCount(  detection_tbl )

    # Using {detection_tbl} table with {table_row_count} records for compression. Please Wait...
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
    
    # Export the compressed detections to a file
    ExportTable(detection_tbl, os.path.join(data_directory, export_compr_file))

    # Output messages
    # Table {detection_tbl} compressed in table mv_anm_compressed with {compressed_count} records.
    print msgs.get_message(index=72, params=[detection_tbl, compressed_count])
    # Compressed detection file exported to: {export_compr_file}.
    print msgs.get_message(index=73, params=[export_compr_file])
    
    # Close connections
    database.table_maintenance(reqcode='reqdisconn')
    