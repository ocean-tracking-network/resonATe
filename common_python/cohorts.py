# -*- coding: utf-8 -*-

import ConfigParser
import argparse
import os
import sys

from library.pg_connection import createConnection
import library.verifications as verify
#import FileCount, FileVersionID, TableExists, Filename, TableCount, FileExists, FileHeaders
# MandatoryColumns
import library.load_to_postgresql as load_to_pg
import library.verify_columns as verify_columns

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

import MessageDB as mdb
msgs = mdb.MessageDB()
from csf.file_io import fileIO

import table_maintenance as tm

def CohortRecords(interval_time=60, compressed_file='',
				  data_directory=DATADIRECTORY):
	'''
	Function to determine cohorts from a compresseed detection file
	:param input_file: compressed detection file
	:param interval_time: The time used to determine whether two or more animals are cohorts
	:return: return result of cohort detections
	'''
	# Variable assignment
	interval_time = interval_time
	data_directory = data_directory
	compressed_file_path = os.path.join(data_directory, compressed_file)

	# Create connection object
	dbconn = tm.table_maintenance()

	# Check if file exists
	if compressed_file == '': compressed_file = None
	if not (compressed_file and verify.FileExists(compressed_file_path)):
		# File {compressed_file} does not exist
		print msgs.get_message(index=19, params=[compressed_file])
		return False

	# missing_columns = ['catalognumber',]
	# if missing_columns:
	#     print msgs.get_message(index=16,params=[missing_columns,compressed_file_path])

	print msgs.get_message(112,['compressed detections', compressed_file]),

	#CSV File validation
	compressed_fileh = fileIO('reqopen', compressed_file_path )

	# Read first line into header
	compressed_headers = compressed_fileh.fileIO('reqread1', fromto=':list:')

	errors = verify_columns.verify_columns('reqcompressed', compressed_fileh, compressed_headers)

	if errors:
			# ERROR!
			print msgs.get_message(114,[])
			for error in errors:
				print error
			print 'Exiting...'
			return -1
	else:
			# OK!
			print msgs.get_message(113,[])

	compressed_fileh.close_file()

	# Create Table
	load_to_pg.createTable('compressed_data_temp', compressed_headers, drop=True)

	# Load the data into the table
	is_loaded = load_to_pg.loadToPostgre('compressed_data_temp', compressed_file_path)

	# Create cursor object
	conn, cur = createConnection()

	# SQL used to create cohort export
	cohort_sql = """
	COPY (
		select fst.catalognumber as anml_1 ,fst.seq_num as anml_1_seq,snd.station
		, snd.catalognumber as anml_2,snd.seq_num as anml_2_seq
		,snd.startdate::timestamp as anml_2_arrive,snd.enddate::timestamp as anml_2_depart
		,snd.startunqdetecid as anml_2_startunqdetecid, snd.endunqdetecid as anml_2_endunqdetecid
		,snd.total_count as anml_2_detcount
		from (select * from compressed_data_temp where startunqdetecid not like '%-release') fst
		join (select * from compressed_data_temp) snd
		on  fst.catalognumber < snd.catalognumber
		and fst.station = snd.station
		and (snd.startdate::timestamp between (fst.startdate::timestamp - interval'{0} minutes')
									 and (fst.enddate::timestamp + interval'{0} minutes')
			or snd.enddate::timestamp between (fst.startdate::timestamp - interval'{0} minutes')
									 and (fst.enddate::timestamp + interval'{0} minutes'))
		order by 1,2,3,4
	) TO STDOUT WITH CSV HEADER QUOTE AS '"';
	""".format(interval_time)

	# Path name & File handler creation
	file_name = '{0}_cohort_{1}min.csv'.format(compressed_file.replace('.csv', ''), interval_time)
	file_path = os.path.join(data_directory, file_name)
	fh = open(file_path, 'wb')

	# Export Data
	cur.copy_expert(cohort_sql, fh)
	fh.close()

	# Close the database connections
	cur.close()
	conn.close()

	# Count the number of records in the file
	file_count = verify.FileCount(file_path, header=True)

	# Print final message to console
	print msgs.get_message(index=60,params=[file_name, file_count])
