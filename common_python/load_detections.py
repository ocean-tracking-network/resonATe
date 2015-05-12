import os

#Local Imports
import library.verifications as verify
import library.load_to_postgresql as load_to_pg
import library.copy_from_postgresql as copy_from_pg

def loadDetections(detection_file, version_id, DistanceMatrix, 
                   ReloadInputFile, SuspectDetections, time_interval,
                   detection_radius, data_directory='/home/sandbox/RStudio/data/'):

    tables_created = {}
    #Is the supplied detection_file variable is valid
    if not verify.Filename( detection_file ):
        print 'Error: [detection_file] variable supplied either has invalid characters or does not contain a csv file extension'
        return -1
        
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
            print 'version_id mismatch {} != {}'.format(file_version_id, input_version_id)
            return -1
        
    #reformat both input_version_id and base_name
    input_version_id = input_version_id.rjust(2,'0') # Zero pad version ID
    base_name = base_name.lower().replace(' ','_')   # Replace spaces with underscores
    
    #Assign table names
    detection_tbl = '{0}_v{1}'.format( base_name, input_version_id )
    matrix_tbl    = '{0}_distance_matrix_v{1}'.format( base_name, input_version_id )
    suspect_tbl   = '{0}_suspect_v{1}'.format( base_name, input_version_id )
    
    #Assign file names
    detection_filename = os.path.join(data_directory,detection_file)
    suspect_filename = os.path.join(data_directory,suspect_tbl+'.csv' )
    matrix_filename = os.path.join(data_directory,matrix_tbl+'.csv' )
    
    #Has the detections table been already loaded?
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
    
    #If the detection table doesn't exist or if realoadfile == True then create detection table
    if not detection_tbl_exists or ReloadInputFile:
        #Extract headers
        detection_headers =  verify.FileHeaders( detection_filename )
        
        #Report duplicate headers
        duplicate_headers = verify.CheckDuplicateHeader( detection_headers )
        if duplicate_headers:
            print 'Duplicate header names: \"{0}\", please rename the duplicate header(s) and rerun.'.format(','.join(duplicate_headers))
        
        #Verify mandatory columns exist
        mandatory_columns = [u'station',
                             u'unqdetecid',
                             u'datecollected',
                             u'catalognumber']
        if DistanceMatrix:
            mandatory_columns.extend([u'longitude',u'latitude'])
        
        missing_columns = verify.MandatoryColumns(detection_headers, mandatory_columns)
        errors = []
        
        if missing_columns:
            errors.append('Error: Mandatory column(s) missing ({})'.format(','.join(missing_columns)))
            #IF the matrix option are defined and one or more of the required columns are missing
            if len(missing_columns) <= 2 and ('latitude' in missing_columns or 'longitude' in missing_columns):
                errors.append('''Error: The required column(s) for creating the station distance matrix are missing:\nSet the DistanceMatrix to FALSE to continue processing with your current data file.'''.format(','.join(missing_columns)))
        else:
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

                #Check for duplicate unique ids
                copy_from_pg.ReturnDuplicates( detection_tbl, 'unqdetecid')
                duplicates = verify.TableCount( 'duplications' )
                
                #If duplicates are found, end execution of the loading script
                if duplicates > 0:
                    duplicate_filepath = os.path.join(data_directory,'{0}_duplicates_v{1}.csv'.format( base_name, input_version_id ))
                    copy_from_pg.ExportTable( 'duplications', duplicate_filepath )
                    errors.append('Error: All unqdetecid(s) are not unique.')
                    errors.append('unqdetecid duplicates exported to \'{0}\''.format( duplicate_filepath ))
                    #Remove Database Tables
                    load_to_pg.removeTable( 'duplications' )
                    load_to_pg.removeTable( detection_tbl )
                else:
                    detection_count = verify.TableCount( detection_tbl )
                    print 'File loaded successfully! Detection Count: {}'.format(detection_count)
            else:
                errors.append('Error loading detections.')
                load_to_pg.removeTable( detection_tbl )
            
        #Print all csv file validation errors and then exit
        if errors:
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
    
