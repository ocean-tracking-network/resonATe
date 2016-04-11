import os
import sys

#Local Imports
import library.verifications as verify
import library.load_to_postgresql as load_to_pg
import library.copy_from_postgresql as copy_from_pg

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

def filterDetections(detection_file, version_id, SuspectFile,
					 OverrideSuspectDetectionFile, DistanceMatrix,
					 detection_radius, ReloadInputFile,
					 data_directory=DATADIRECTORY):
	'''
	Run the process for filtering the detection files using the supplied suspect detection file.
	'''
	mandatory_columns = ['station',
						 'unqdetecid',
						 'datecollected',
						 'catalognumber'] # List of mandatory column names for detectiuon_file
	susp_mandatory_columns = ['suspect_detection', 'row_num', 'input_interval']

	#Variable validation
	if not verify.Filename(detection_file):
		return 'Error: [detection_file] variable has invalid characters or is not a csv file'

	#version_id supplied in the filename?
	file_version_id = verify.FileVersionID( detection_file )
	if file_version_id:
		#remove the version_id & extension from the filename
		base_name = detection_file[:-8]
	else:
		#remove the extension from the filename
		base_name = detection_file[:-4]

	#Check all version_id combinations and apply to input_version_id
	input_version_id = verify.VersionID( version_id )
	if file_version_id and not input_version_id:
		input_version_id = file_version_id
	elif not file_version_id and not input_version_id:
		input_version_id = '00'
	elif file_version_id and input_version_id:
		if file_version_id != input_version_id:
			return 'version_id mismatch {} != {}'.format(file_version_id, input_version_id)

	#reFormat both input_version_id and base_name
	input_version_id = input_version_id.rjust(2,'0')
	base_name = base_name.lower().replace(' ','_')

	detection_file_path = os.path.join(data_directory, detection_file )

	#Check to see if input file exists
	if not verify.FileExists( detection_file_path ):
		return 'File \'{0}\' does not exist.'.format(detection_file)

	#Set the suspect detection filename
	if SuspectFile and OverrideSuspectDetectionFile:
		suspect_file = SuspectFile
	else:
		suspect_file = '{0}_suspect_v{1}.csv'.format(base_name, input_version_id.rjust(2,'0'))

	#Check if the file exists in either the export and import folders
	suspect_file_path = os.path.join(data_directory, suspect_file )

	#user the file in the input folder before the export
	if not verify.FileExists( suspect_file_path ):
		return 'File {0} does not exist.'.format(suspect_file)

	print 'Using suspect detection file: {0}'.format(suspect_file_path)

	#Set the table and file names
	detection_tbl = '{0}_v{1}'.format( base_name, input_version_id )
	output_tbl = '{0}_v{1}'.format( base_name, str(int(input_version_id)+1).rjust(2,'0') )
	matrix_tbl = '{0}_distance_matrix_v{1}'.format(base_name,str(int(input_version_id)+1).rjust(2,'0'))
	matrix_file_name = os.path.join(data_directory, matrix_tbl + ".csv").format(data_directory, matrix_tbl )
	output_file_name = '{0}_v{1}.csv'.format(base_name,str(int(input_version_id)+1).rjust(2,'0'))
	output_file_path = os.path.join(data_directory, output_file_name)

	#Does output file exist?
	if os.path.isfile( output_file_path ):
		outputfile_count = verify.FileCount( output_file_path, header=True )
		print """Filter Output file already exists named "{0}" with {1} records.""".format( output_file_path , outputfile_count)
		return "Please rename or delete output file."

	#Does matrix file exist?
	if DistanceMatrix and os.path.isfile( matrix_file_name ):
		matrixfile_count = verify.FileCount( matrix_file_name, header=True )
		print """Station distance matrix output file already exists named "{0}" with {1} records.""".format( matrix_file_name , matrixfile_count)
		return "Please rename or delete output file or set \"DistanceMatrix = FALSE\" to proceed with current data."

	#Retrieve csv csv_headers information from the detections file
	csv_headers_det = verify.FileHeaders(detection_file_path)
	csv_headers_susp = verify.FileHeaders(suspect_file_path)
	error_lst = []

	#If user is missing mandatory column raise an error
	missing_columns_det = verify.MandatoryColumns(csv_headers_det, mandatory_columns)
	if missing_columns_det:
		error_lst.append('Error: Mandatory column(s) missing from file {0}:({1})'.format(detection_file_path,','.join(missing_columns_det)))

	missing_columns_susp = verify.MandatoryColumns(csv_headers_susp, susp_mandatory_columns)
	if missing_columns_susp:
		error_lst.append('Error: Mandatory column(s) missing from file {0}:({1})'.format(suspect_file_path,','.join(missing_columns_susp)))

	if 'unqdetecid' not in missing_columns_det:
		if verify.TableExists( detection_tbl ) and not ReloadInputFile:
			detection_tbl_count = verify.TableCount( detection_tbl )
			print '''file "{0}" already loaded with {1} records.'''.format( detection_file, detection_tbl_count )
			detections_loaded = True
		elif not verify.TableExists( detection_tbl ) or ReloadInputFile:
			#Remove old table and reload data
			if ReloadInputFile and verify.TableExists( detection_tbl ):
				load_to_pg.removeTable( detection_tbl )

			#Report duplicate headers
			duplicate_headers = verify.CheckDuplicateHeader( csv_headers_det )

			if duplicate_headers:
				print 'Duplicate header names: \"{0}\" in input_file \"{1}\", please rename the duplicate header(s) and rerun.'.format(','.join(duplicate_headers),detection_file)

			#Load table
			table_created = load_to_pg.createTable( detection_tbl, csv_headers_det)

			#Exit if table could not be created
			if not table_created:
				return 'Exiting...'

			#Load table contents
			detections_loaded = load_to_pg.loadToPostgre( detection_tbl, detection_file_path )

			if detections_loaded:
				#Check for duplicate unqdetecid
				copy_from_pg.ReturnDuplicates( detection_tbl, 'unqdetecid')
				duplicates = verify.TableCount( 'duplications' )

				#If duplicates are found, end execution of the loading script
				if duplicates > 0:
					duplicate_filepath = '{0}{1}_duplicates_v{2}.csv'.format(data_directory, base_name, input_version_id.rjust(2,'0') )
					copy_from_pg.ExportTable( 'duplications', duplicate_filepath )
					error_lst.append('Error: All unqdetecid(s) are not unique.')
					error_lst.append('unqdetecid duplicates exported to \'{0}\''.format( duplicate_filepath ))
					load_to_pg.removeTable( 'duplications' )

				count_det = verify.TableCount( detection_tbl )
				print('Input detection file contains {0} records'.format(count_det))
			else:
				error_lst.append('Error loading detections.')
				load_to_pg.removeTable( detection_tbl )

		susp_duplicate_headers = verify.CheckDuplicateHeader( csv_headers_susp )

		if susp_duplicate_headers:
			print 'Duplicate header names: \"{0}\" in input_file \"{1}\", please rename the duplicate header(s) and rerun.'.format(','.join(susp_duplicate_headers),suspect_file)

		if detections_loaded:
			#Load suspect detections
			susp_table_created = load_to_pg.createTable( 'suspects', csv_headers_susp, drop=True)

			#Exit if table could not be created
			if not susp_table_created:
					return 'Exiting...'

			suspect_loaded = load_to_pg.loadToPostgre( 'suspects', suspect_file_path )
			#If suspect table could not be loaded append error
			if not suspect_loaded:
				error_lst.append('Error loading suspect detections.')
				load_to_pg.removeTable( 'suspects' )

	#Print all csv file validation errors and then exit
	if error_lst:
		for error in error_lst:
			print error
		return 'Exiting...'

	#Create final output file
	copy_from_pg.copyTableStructure(detection_tbl, output_tbl, drop=True)
	load_to_pg.removeSuspect( detection_tbl, 'suspects', output_tbl)
	count_removed_detection = verify.tableDifference( detection_tbl, output_tbl )
	count_output = verify.TableCount( output_tbl )
	copy_from_pg.ExportTable(output_tbl, output_file_path)

	#Create a dataframe with none of the suspected detections
	print "{0} suspect detections removed".format(count_removed_detection)
	print "Total detections in output file: {0}".format(count_output)
	print 'Detection file saved to: ({0})'.format(output_file_path)

	if DistanceMatrix:
		# Remove existing Distance Matrix Table
		if verify.TableExists( matrix_tbl ):
			load_to_pg.removeTable( matrix_tbl )

		# Create distance matrix table
		load_to_pg.createMatrix( output_tbl, matrix_tbl, detection_radius)

		# Get count and set filename
		matrix_count = verify.TableCount( matrix_tbl )
		matrix_filename = "{0}{1}.csv".format( data_directory, matrix_tbl )

		copy_from_pg.ExportTable( matrix_tbl, matrix_file_name)

		# Print summary of actions to console
		print 'Station distance matrix exported to: {0}'.format(matrix_file_name)
		print 'There are {0} station matrix pairs'.format(matrix_count)

	#Calculate the script processing time
	return 'Filtering complete.'
