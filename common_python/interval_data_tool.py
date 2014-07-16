import sys
import os 

# System paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CSF_PATH = os.path.join(SCRIPT_PATH, os.pardir, 'csf')

sys.path.append(CSF_PATH)

# Import CSF/library scripts
from Table import message as msg
from file_io import fileIO
from database_io import databaseIO
from table_maintinance import table_maintinance
from build_filename import build_filename

# Library Modules
from library import verify_columns
from library import compress_detections
from library import view_intvl
from library import putfile

def intervalData(detection_filename, dist_matrix_filename, data_directory = '/home/sandbox/RStudio/data/'):
    '''
    Interval data tool, given distance_matrix and detection file, export compressed detection and interval data files
    '''
    # Variable Assignments 
    det_column_errors = [] # (list of str) verification errors from the detection file
    dis_mtx_column_errors = [] # (list of str) verification errors from distance matrix file
    detection_filepath = os.path.join(data_directory, detection_filename) # (str) Set abosolute path for detection file
    dis_mtx_filepath = os.path.join(data_directory, dist_matrix_filename) # (str) Set abosolute path for distance matrix file
    detection_fileh = None
    dis_mtx_fileh = None
    db = None # Database connection pointer
    missing_files = [] # Accumulate a list of missing files
    det_load_error = False
    mtx_load_error = False
    
    ##### Verification Step #####
    
    # Determine the output name for the compressed file
    compressed_filename = build_filename('reqcompressed', detection_filename)
    compressed_filepath = os.path.join(data_directory, compressed_filename)
    
    # Determine output name for the interval data file
    interval_data_filename = build_filename('reqinterval', detection_filename)
    interval_data_filepath = os.path.join(data_directory, interval_data_filename)
    
    # Test to see if the files exist
    compressed_exists =  fileIO().fileIO('reqexist', compressed_filepath )
    interval_data_exists =  fileIO().fileIO('reqexist', interval_data_filepath )
    
    # Exit program if export files of the same name exist
    if compressed_exists or interval_data_exists:
        if compressed_exists:
            print '{0}'.format(msg(requestCode='simple', index=103, 
                             numbOfParameters=1, param1=compressed_filepath))
        if interval_data_exists:
            print '{0}'.format(msg(requestCode='simple', index=103, 
                             numbOfParameters=1, param1=interval_data_filepath))
        print '{0}'.format(msg(requestCode='simple', index=104,numbOfParameters=0 ))
        return ''
    
    # Load and verify detection file
    if fileIO().fileIO('reqexist', detection_filepath):
        # Verifying Detection file: 
        print msg(requestCode='simple', index=112, 
                               numbOfParameters=2, param1='Detection', param2=detection_filename),
        detection_fileh = fileIO('reqopen', detection_filepath )
        detection_file_header = detection_fileh.fileIO('reqread1',fromto=':list:')
        det_column_errors = verify_columns.verify_columns('reqdetect', detection_fileh, detection_file_header)
        if det_column_errors:
            # ERROR
            print msg(requestCode='simple', index=114,numbOfParameters=0)
        else:
            # OK
            print msg(requestCode='simple', index=113,numbOfParameters=0)
    else:
        missing_files.append(detection_filename)
    
    # Load and verify distance matrix file
    if fileIO().fileIO('reqexist', dis_mtx_filepath):
        # Verifying Distance Matrix file: 
        print msg(requestCode='simple', index=112, 
                               numbOfParameters=2, param1='Distance Matrix', param2=dist_matrix_filename),
        dis_mtx_fileh = fileIO('reqopen', dis_mtx_filepath )
        dis_mtx_file_header = dis_mtx_fileh.fileIO('reqread1', fromto=':list:')
        dis_mtx_column_errors = verify_columns.verify_columns('reqdistmtrx', dis_mtx_fileh, dis_mtx_file_header)
        if dis_mtx_column_errors:
            # ERROR
            print msg(requestCode='simple', index=114,numbOfParameters=0)
        else:
            # OK
            print msg(requestCode='simple', index=113,numbOfParameters=0)
    else:
        missing_files.append(dist_matrix_filename)
    
    # Return if any of the files are missing
    if missing_files:   
        for f in missing_files:
            print msg('simple',19,
                              1,param1=f)
    
    # Return verification errors
    if det_column_errors or dis_mtx_column_errors:
        # Constuct output errors into a single list
        output_errors = det_column_errors[:]
        output_errors.extend(dis_mtx_column_errors) # Combine column errors from both files
        for error in output_errors:
            print error # Output errors
            
    # If Errors, exit 
    if det_column_errors or dis_mtx_column_errors or missing_files:
        return '' # Program exit
    
    # Close the detection_file and the distance_matrix file
    detection_fileh.fileIO('reqclose')
    dis_mtx_fileh.fileIO('reqclose')
    
    ##### Loading Step #####
    
    # Open database connection
    db =  table_maintinance('reqconn')
    
    # Drop the mv_anm_detections table if it exists.
    anm_tbl_exists =  db.table_maintinance(reqcode='reqexist', tablename='mv_anm_detections')
    if anm_tbl_exists:
        db.table_maintinance(reqcode='reqdropcscd', tablename='mv_anm_detections')
    
    # Drop the distance_matrix table if it exists.
    dis_mtx_tbl_exits = db.table_maintinance(reqcode='reqexist', tablename='distance_matrix')
    if dis_mtx_tbl_exits:
        db.table_maintinance(reqcode='reqdropcscd', tablename='distance_matrix')
        
    # Create mv_anm_detections table
    db.table_maintinance(reqcode='reqcreate', 
                         tablename='mv_anm_detections', filename=detection_file_header)
    
    # Load mv_anm_detections csv
    # Loading detection file:
    print msg(requestCode='simple', index=115, 
                           numbOfParameters=2, param1='Detection', param2=detection_filename),
    det_load_error = db.table_maintinance(reqcode='reqload', tablename='mv_anm_detections', filename=detection_filepath)
    if det_load_error:
        print msg(requestCode='simple', index=114,numbOfParameters=0)
        print msg(requestCode='simple', index=99, numbOfParameters=1, param1=det_load_error)
    else:
        print msg(requestCode='simple', index=113,numbOfParameters=0)
        
    
    # Create distance matrix table
    db.table_maintinance(reqcode='reqcreate',tablename='distance_matrix', filename=dis_mtx_file_header)
    
    # Load distance matrix table
    print msg(requestCode='simple', index=115, 
                           numbOfParameters=2, param1='Distance Matrix', param2=dist_matrix_filename),
    mtx_load_error = db.table_maintinance(reqcode='reqload', tablename='distance_matrix', filename=dis_mtx_filepath)
    if mtx_load_error:
        print msg(requestCode='simple', index=114, numbOfParameters=0)
        print msg(requestCode='simple', index=99, numbOfParameters=1, param1=mtx_load_error)
    else:
        print msg(requestCode='simple', index=113, numbOfParameters=0)
    
    ##### Processing Step #####
    
    # Compress the detection data
    compress_detections.compress_detections()
    
    # Create interval view
    view_intvl.view_intvl()
    
    ##### File Output Step #####
    print msg('simple',118,0),
    
    # Create local copies of tables 
    try:
        count_compressed = putfile.putFile('reqtabcsv', 'mv_anm_compressed', compressed_filepath)
        count_interval = putfile.putFile('reqtabcsv', 'vw_interval_data', interval_data_filepath)
        print msg(requestCode='simple', index=113,numbOfParameters=0)
    except Exception, e:
        print msg(requestCode='simple', index=114,numbOfParameters=0)
        print msg(requestCode='simple', index=100,numbOfParameters=1,param1=e)
        
    # Final export report messages 
    print msg('simple',116,2,param1=compressed_filename,param2=count_compressed)
    print msg('simple',117,2,param1=interval_data_filename, param2=count_interval)
    return '' # Program exit
    
#if __name__ == '__main__':
#    data_directory = 'W:\\RStudio\\data\\'
#    detection_filename = 'detections.csv'
#    dist_matrix_filename = 'sample_matched_detections_2013_distance_matrix_v01_merged.csv'
#    intervalData(detection_filename, dist_matrix_filename, data_directory)
    