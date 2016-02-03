# -*- coding: utf-8 -*-
"""
Distance matrix merge module v2

Author: Brian Jones
Version: 2.0
"""

import os
import sys
import pandas as pd

# Get paths
SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

d = open('common_python/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

#Local Imports
import library.verifications as verify
import library.verify_columns as verify_columns

import MessageDB as mdb
msgs = mdb.MessageDB()
from csf.file_io import fileIO

def dis_mtx_merge(reqcode, distance_matrix_input, distance_real_input,
				  data_directory=DATADIRECTORY):

	# Variable Assignments
	reqcode = reqcode
	distance_matrix_input = distance_matrix_input
	distance_real_input = distance_real_input
	data_directory = data_directory

	# Check if reqcode is valid
	if(reqcode !='reqmerge'):
		# return 'Error:Not valid reqcode'  #CSF
		print msgs.get_message(12,[reqcode])
		return -1

	# Check for valid filenamesl
	if not verify.Filename( distance_matrix_input ):
		# return 'Error: {distance_matrix_input} variable supplied either
		#             has invalid characters or does not contain a csv
		#             file extension'
		print msgs.get_message(15,[distance_matrix_input])
		return -1

	if not verify.Filename( distance_real_input ):
		# return 'Error: {distance_real_input} variable supplied either
		#             has invalid characters or does not contain a csv
		#             file extension'
		print msgs.get_message(15,[distance_real_input])
		return -1

	# Create output file name & full path
	output_file = os.path.splitext(distance_matrix_input)[0]+'_merged.csv'
	output_file_path = os.path.join(data_directory, output_file)

	# Assign file paths
	distance_matrix_input_path = os.path.join(data_directory,
											  distance_matrix_input)
	distance_real_input_path = os.path.join(data_directory,
											distance_real_input)

	# Check if both files exist
	if not verify.FileExists( distance_matrix_input_path ):
		# return: 'File {distance_matrix_input_path} does not exist'
		print msgs.get_message(index=19,params=[distance_matrix_input_path])
		return -1

	if not verify.FileExists( distance_real_input_path):
		# return: 'File {distance_real_input_path} does not exist'
		print msgs.get_message(index=19,params=[distance_real_input_path])
		return -1

	# Verify both matrix input files
	print msgs.get_message(112,['distance matrix',distance_matrix_input]),

	#CSV File validation
	matrix_fileh = fileIO('reqopen', distance_matrix_input_path )

	# Read first line into header
	matrix_headers = matrix_fileh.fileIO('reqread1', fromto=':list:')

	matrix_errors = verify_columns.verify_columns('reqdistmtrx',
											matrix_fileh, matrix_headers)
	matrix_fileh.close_file()

	#Print all csv file validation errors and then exit
	if matrix_errors:
		# ERROR!
		print msgs.get_message(114,[])
		for error in matrix_errors:
			print error
	else:
		# OK!
		print msgs.get_message(113,[])

	print msgs.get_message(112,['distance real',distance_real_input]),

	real_fileh = fileIO('reqopen', distance_real_input_path )
	real_headers = real_fileh.fileIO('reqread1', fromto=':list:')

	real_errors = verify_columns.verify_columns('reqrealdistmtrx',
											real_fileh, real_headers)

	real_fileh.close_file()

	if real_errors:
		# ERROR!
		print msgs.get_message(114,[])
		for error in real_errors:
			print error
	else:
		# OK!
		print msgs.get_message(113,[])

	if real_errors or matrix_errors:
		print 'Exiting...'
		return -1

	# Open the two files as pandas DataFrames
	matrix_df = pd.read_csv(distance_matrix_input_path, dtype='object')
	real_df = pd.read_csv(distance_real_input_path, dtype='object')

	updates = 0

	# Field update function (DRY)
	def field_update(df1, df2, field):
		'''
		return: number of updates
		'''
		updates = 0
		for index, row in df2[df2[field].notnull()].iterrows():
			df_index = df1.loc[((df1['stn1'] == row['stn1']) &
								(df1['stn2'] == row['stn2'])) |
							   ((df1['stn2'] == row['stn1']) &
								(df1['stn1'] == row['stn2']))]

			# continue only if station pair could be matched
			if not df_index.empty:
				for i, r in df_index.iterrows():
					if df1.loc[i, field] != row[field]:
						df1.loc[i, field] = row[field]
						updates += 1

		return updates

	# Update real_distance
	updates += field_update(matrix_df, real_df, 'real_distance')
	# Update detec_radius1
	updates += field_update(matrix_df, real_df, 'detec_radius1')
	# Update detec_radius2
	updates += field_update(matrix_df, real_df, 'detec_radius2')

	# Output merged file if update are performed
	if updates > 0:
		# print: There are {updates} records updated in file {output_file}
		print msgs.get_message(index=18, params=[updates, output_file])
		# Export the merged file
		matrix_df.to_csv(output_file_path, index= False)
	else:
		# print: There is no records update in {distance_matrix_input}
		print msgs.get_message(index=22, params=[distance_matrix_input])

	# return: Updates complete
	print msgs.get_message(index=23)
	return 1

if __name__ == '__main__':
	print dis_mtx_merge('reqmerge', 'matrix.csv','matrix_update.csv')
