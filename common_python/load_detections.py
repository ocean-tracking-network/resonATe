import os
import sys

#Local Imports
import library.verifications as verify
import library.load_to_postgresql as load_to_pg
import library.copy_from_postgresql as copy_from_pg
import library.verify_columns as verify_columns

# Append the CSF path
SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

#Load message module
import MessageDB as mdb
msgs = mdb.MessageDB()
from csf.file_io import fileIO

def loadDetections(detection_file, version_id, DistanceMatrix,
				   ReloadInputFile, SuspectDetections, time_interval,
				   detection_radius, data_directory=DATADIRECTORY):

	tables_created = {}
	#Is the supplied detection_file variable is valid, quit if not
	if not verify.Filename( detection_file ):
		#'Error: [detection_file] variable supplied either has invalid characters or does not contain a csv file extension'
		msgs.get_message(15,[detection_file])
		return -1

	# extract the version_id, if supplied by the filename?
	file_version_id = verify.FileVersionID( detection_file )
	if file_version_id:
		#remove the version_id & extension from the filename
		base_name = detection_file[:-8]
	else:
		#remove the extension from the filename
		base_name = detection_file[:-4]

	# Check all version_id combinations and apply to input_version_id
	input_version_id = verify.VersionID( version_id )
	if file_version_id and not input_version_id:
		input_version_id = file_version_id
	elif not file_version_id and not input_version_id:
		input_version_id = '00'
	elif file_version_id and input_version_id:
		if file_version_id != input_version_id:
			print 'version_id mismatch {} != {}'.format(file_version_id, input_version_id)
			return -1

	# Reformat both input_version_id and the file base_name
	input_version_id = input_version_id.rjust(2,'0') # Zero pad version ID
	base_name = base_name.lower().replace(' ','_')   # Replace spaces with underscores

	# Assign table names
	detection_tbl = '{0}_v{1}'.format( base_name, input_version_id )
	matrix_tbl    = '{0}_distance_matrix_v{1}'.format( base_name, input_version_id )
	suspect_tbl   = '{0}_suspect_v{1}'.format( base_name, input_version_id )

	# Assign file names
	detection_filename = os.path.join(data_directory,detection_file)
	suspect_filename = os.path.join(data_directory,suspect_tbl+'.csv' )
	matrix_filename = os.path.join(data_directory,matrix_tbl+'.csv' )

	detection_tbl_exists =  verify.TableExists( detection_tbl )

	# Return if detection_file does not exist
	if not verify.FileExists( detection_filename ):
		print '''File "{0}" does not exist.'''.format( detection_filename )
		print 'Please ensure that the file is in the data folder or check the detection_file variable.'
		return -1
	# Send a message if using the table in the database
	if detection_tbl_exists and not ReloadInputFile:
		detection_tbl_count = verify.TableCount( detection_tbl )
		print '''Table "{0}" already loaded with {1} records.'''.format( detection_tbl, detection_tbl_count )

	#Does matrix file already exist on the file system?
	if DistanceMatrix and verify.FileExists(  matrix_filename ):
		matrixfile_count = verify.FileCount( matrix_filename, header=True )
		print """Station distance matrix output file already exists named "{0}" with {1} records.""".format( matrix_filename , matrixfile_count)
		print "Please rename or delete output file or set \"DistanceMatrix = FALSE\" to proceed with current data."
		return -1
	#Does suspect file exist on the file system?
	if SuspectDetections and verify.FileExists( suspect_filename ):
		suspectfile_count = verify.FileCount( suspect_filename, header=True )
		print """Suspect detection output file already exists named "{0}" with {1} records.""".format( suspect_filename , suspectfile_count)
		print """Please rename or delete output file or set \"SuspectDetections = FALSE\" to proceed with current data."""
		return -1

	#Check the detection_radius variable for a correct value, if entered: 0 to 999
	if not detection_radius == '':
		try:
			if int(detection_radius) not in range(1000):
				raise
		except:
			print """Value for detection_radius is not correct, must be between 0 and 999"""
			return -1

	#If the detection table doesn't exist or if ReloadInputFile == True, create detection table
	if not detection_tbl_exists or ReloadInputFile:
		#CSV File validation
		detection_fileh = fileIO('reqopen', detection_filename )

		# Read first line into header
		detection_headers = detection_fileh.fileIO('reqread1', fromto=':list:')
		print msgs.get_message(112,['detection',detection_file]),

		errors = verify_columns.verify_columns(('reqdetect_w_distmtrx' if
											 DistanceMatrix else 'reqdetect'),
											detection_fileh, detection_headers)

		detection_fileh.close_file()

		if not errors:
			# OK!
			print msgs.get_message(113,[])

			#Create detections table
			table_created = load_to_pg.createTable(detection_tbl, detection_headers, ReloadInputFile) # final argument says whether to destroy an existing table.

			#Exit if table could not be created
			if not table_created:
				print 'Exiting...'
				return -1
			else:
				tables_created['detections'] = detection_tbl

			#Load the table contents with csv file
			detections_loaded = load_to_pg.loadToPostgre( detection_tbl, detection_filename)

			if detections_loaded:
				#Remove blank lines from the newly created table
				load_to_pg.removeNullRows(detection_tbl, 'unqdetecid')

				# Check file/table for lat/lon and Well Known Text/Binary and return a list of all newly created geometry columns.
				geometry_columns = load_to_pg.createGeometryColumns(detection_tbl)

				#If duplicates are found, end execution of the loading script
				detection_count = verify.TableCount( detection_tbl )
				print 'File loaded successfully! Detection Count: {}'.format(detection_count)

			else:
				errors.append('Error loading detections.')
				load_to_pg.removeTable( detection_tbl )

		#Print all csv file validation errors and then exit
		if errors:
			# ERROR!
			print msgs.get_message(114,[])
			for error in errors:
				print error
			print 'Exiting...'
			return -1

	if SuspectDetections:
		#Has the suspect detections table been created?
		if verify.TableExists( suspect_tbl ):
			#Remove table
			load_to_pg.removeTable( suspect_tbl )

		#Load Suspect Detections
		load_to_pg.createSuspect(detection_tbl, suspect_tbl, time_interval)

		#Get count and create filename
		suspect_count = verify.TableCount( suspect_tbl )
		#Export Suspect Detection Summary
		copy_from_pg.ExportTable( suspect_tbl, suspect_filename)

		tables_created['suspect'] = suspect_tbl
		#Print summary of actions to console
		print 'Detection summary exported to: {0}'.format(suspect_filename)
		print 'There are {0} suspect detections'.format(suspect_count)

	if DistanceMatrix:
		# Has the distance matrix table been created?
		if DistanceMatrix and verify.TableExists( matrix_tbl ):
			# Remove table
			load_to_pg.removeTable( matrix_tbl )

		# Create array sorting function
		load_to_pg.createArraySort()

		# Load Distance Matrix
		matrix_created = load_to_pg.createMatrix(detection_tbl, matrix_tbl, detection_radius)

		if matrix_created:
			# Get count and create filename
			matrix_count = verify.TableCount( matrix_tbl )
			# Export Distance Matrix
			copy_from_pg.ExportTable( matrix_tbl, matrix_filename)
			tables_created['dist_matrix'] = matrix_tbl
			#Print summary of actions to console
			print 'Station distance matrix exported to: {0}'.format(matrix_filename)
			print 'There are {0} station matrix pairs'.format(matrix_count)
		else:
			#Program exit on error
			print 'Exiting...'
			return -1
	print 'Loading complete. Created/populated %s tables' % len(tables_created)
	return tables_created

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Load a csv file into the "\
									 "database.")
	parser.add_argument('-detection_file')
	parser.add_argument('-version_id')
	parser.add_argument('-time_interval')
	parser.add_argument('-SuspectDetections')
	parser.add_argument('-DistanceMatrix')
	parser.add_argument('-ReloadInputFile')

	args = parser.parse_args()

	loadDetections(detection_file= args.detection_file,
				   version_id= args.version_id,
				   time_interval= args.time_interval,
				   SuspectDetections= args.SuspectDetections,
				   DistanceMatrix= args.DistanceMatrix,
				   ReloadInputFile= args.ReloadInputFile)
