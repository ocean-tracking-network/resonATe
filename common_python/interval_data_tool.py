import sys
import os 

# System paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
#CSF_PATH = os.path.join(SCRIPT_PATH, os.pardir, 'csf')

sys.path.append(CSF_PATH)

# Import CSF/library scripts
import csf.MessageDB as mdb
msgs = mdb.MessageDB()
from csf.file_io import fileIO
#from csf.database_io import databaseIO
from csf.table_maintenance import table_maintenance
from csf.build_filename import build_filename

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
            print '{0}'.format(msgs.get_message(index=103, params=[compressed_filepath]))
        if interval_data_exists:
            print '{0}'.format(msgs.get_message(index=103, params=[interval_data_filepath]))
        print '{0}'.format(msgs.get_message(index=104))
        return ''
    
    # Load and verify detection file
    if fileIO().fileIO('reqexist', detection_filepath):
        # Verifying Detection file: 
        print msgs.get_message(index=112, params=['Detection', detection_filename]),
        detection_fileh = fileIO('reqopen', detection_filepath )
        detection_file_header = detection_fileh.fileIO('reqread1',fromto=':list:')
        det_column_errors = verify_columns.verify_columns('reqdetect', detection_fileh, detection_file_header)
        if det_column_errors:
            # ERROR
            print msgs.get_message(index=114)
        else:
            # OK
            print msgs.get_message(index=113)
    else:
        missing_files.append(detection_filename)
    
    # Load and verify distance matrix file
    if fileIO().fileIO('reqexist', dis_mtx_filepath):
        # Verifying Distance Matrix file: 
        print msgs.get_message(index=112, params=['Distance Matrix', dist_matrix_filename]),
        dis_mtx_fileh = fileIO('reqopen', dis_mtx_filepath )
        dis_mtx_file_header = dis_mtx_fileh.fileIO('reqread1', fromto=':list:')
        dis_mtx_column_errors = verify_columns.verify_columns('reqdistmtrx', dis_mtx_fileh, dis_mtx_file_header)
        if dis_mtx_column_errors:
            # ERROR
            print msgs.get_message(index=114)
        else:
            # OK
            print msgs.get_message(index=113)
    else:
        missing_files.append(dist_matrix_filename)
    
    # Return if any of the files are missing
    if missing_files:   
        for f in missing_files:
            print msgs.get_message(19, params=[f])
    
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
    db =  table_maintenance('reqconn')
    
    # Drop the mv_anm_detections table if it exists.
    anm_tbl_exists =  db.table_maintenance(reqcode='reqexist', tablename='mv_anm_detections')
    if anm_tbl_exists:
        db.table_maintenance(reqcode='reqdropcscd', tablename='mv_anm_detections')
    
    # Drop the distance_matrix table if it exists.
    dis_mtx_tbl_exits = db.table_maintenance(reqcode='reqexist', tablename='distance_matrix')
    if dis_mtx_tbl_exits:
        db.table_maintenance(reqcode='reqdropcscd', tablename='distance_matrix')
        
    # Create mv_anm_detections table
    db.table_maintenance(reqcode='reqcreate',
                         tablename='mv_anm_detections', filename=detection_file_header)
    
    # Load mv_anm_detections csv
    # Loading detection file:
    print msgs.get_message(index=115, params=['Detection', detection_filename]),
    det_load_error = db.table_maintenance(reqcode='reqload', tablename='mv_anm_detections', filename=detection_filepath)
    if det_load_error:
        print msgs.get_message(index=114)
        print msgs.get_message(index=99, params=[det_load_error])
    else:
        print msgs.get_message(index=113)
        
    
    # Create distance matrix table
    db.table_maintenance(reqcode='reqcreate',tablename='distance_matrix', filename=dis_mtx_file_header)
    
    # Load distance matrix table
    print msgs.get_message(index=115, params=['Distance Matrix', dist_matrix_filename]),
    mtx_load_error = db.table_maintenance(reqcode='reqload', tablename='distance_matrix', filename=dis_mtx_filepath)
    if mtx_load_error:
        print msgs.get_message(index=114)
        print msgs.get_message(index=99, params=[mtx_load_error])
    else:
        print msgs.get_message(index=113)
    
    ##### Processing Step #####
    
    # Compress the detection data
    compress_detections.compress_detections()
    
    # Create interval view
    view_intvl.view_intvl()
    
    ##### File Output Step #####
    print msgs.get_message(118)
    
    # Create local copies of tables 
    try:
        count_compressed = putfile.putFile('reqtabcsv', 'mv_anm_compressed', compressed_filepath)
        count_interval = putfile.putFile('reqtabcsv', 'vw_interval_data', interval_data_filepath)
        print msgs.get_message(index=113)
    except Exception, e:
        print msgs.get_message(index=114)
        print msgs.get_message(index=100,params=[e])
        
    # Final export report messages 
    print msgs.get_message(116, params=[compressed_filename, count_compressed])
    print msgs.get_message(117, params=[interval_data_filename, count_interval])
    return '' # Program exit
    
#if __name__ == '__main__':
#    data_directory = 'W:\\RStudio\\data\\'
#    detection_filename = 'detections.csv'
#    dist_matrix_filename = 'sample_matched_detections_2013_distance_matrix_v01_merged.csv'
#    intervalData(detection_filename, dist_matrix_filename, data_directory)
    