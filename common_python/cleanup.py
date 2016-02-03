import sys
import os

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

DATADIRECTORY = open('datadirectory', 'r')

import MessageDB as mdb
from database_io import databaseIO
msgs = mdb.MessageDB()

def cleanup(reqcode):
	'''
	Clean the database of tables in the public schema
	'''
	reqcode = reqcode

	if reqcode == 'reqcleanup':
		''' Perform cleanup routine '''
		c = databaseIO('reqconn')  # Connect
		c.databaseIO('reqcleanup') # Clean
		c.databaseIO('reqdisconn') # Close
	else:
		print msgs.get_message(12, [reqcode])

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Cleanup PostgreSQL database")
	parser.add_argument('-reqcode', required= True)

	args = parser.parse_args()

	cleanup(args.reqcode)
