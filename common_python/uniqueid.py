import pandas as pd
import os
import sys
import library.verifications as verify
import sqlite3
import codecs
from __builtin__ import str


# System paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CSF_PATH = os.path.join(SCRIPT_PATH, os.pardir, 'csf')
sys.path.append(CSF_PATH)

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

#Import Message DB
import MessageDB as mdb
msgs = mdb.MessageDB()

def add_column_unqdetecid(input_file,
						  data_directory=DATADIRECTORY):

	infile_path = os.path.join(data_directory, input_file)

	# Check to see if infile_path exists and is a csv before proceeding
	if not verify.FileExists(infile_path):
		# File {input_file} does not exist
		print msgs.get_message(index=19, params=[input_file])
		return -1
	elif (not verify.Filename(input_file)):
		# Error: {0} variable supplied either has invalid characters or does not contain a csv file extension
		print msgs.get_message(index=15, params=[input_file])
		return -1

	outfile_name = input_file.replace('.csv','') + '_unqid.csv'
	outfile_path = os.path.join(data_directory, outfile_name)

	# If the output file exists, print an error message
	if verify.FileExists(outfile_path):
		# File {input_file} does not exist
		print msgs.get_message(index=20, params=[outfile_name])
		return -1

	chunksize = 10000
	count = 1

	# Read csv file into pandas
	dataframe = pd.read_csv(open(infile_path, 'rb'), dtype=object, chunksize=chunksize)

	print msgs.get_message(index=112, params=['input_file', input_file]),
	for num, chunk in enumerate(dataframe):
		# Extract header and insert the unqdetecid column
		if num == 0:
			header = chunk.columns.values.tolist()
			# Remove non-ascii
			header = [unicode(x, 'ascii', 'ignore') for x in header]

			# Check to see if column unqdetecid already exists
			if 'unqdetecid' in header:
				# Error
				print msgs.get_message(index=114)
				# Column '{unqdetecid}' already exists, Please use another file.
				print msgs.get_message(index=210, params=['unqdetecid'])
				return -1

			#Insert unqdetecid into header
			header.insert(0, 'unqdetecid')

			# Create the output file and set the header
			with open(outfile_path,'w') as outfile:
				outfile.write(','.join(header) + '\n')

			# OK
			print msgs.get_message(index=113)
			# "Creating file '{outfile_name}' ..."
			print msgs.get_message(index=122, params=[outfile_name]),

		# Create an unique id column
		indexes = pd.DataFrame({'index':range(count, count+min([chunksize,
																len(chunk)]))})

		# Join dataframes
		chunk = indexes.join(chunk)
		chunk.to_csv(outfile_path, index=False, header=False, mode='a')
		count += chunksize

	# OK
	print msgs.get_message(index=113)
