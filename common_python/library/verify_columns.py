import os
import sys
import re
import time 

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CSF_PATH = os.path.join(SCRIPT_PATH, os.pardir,os.pardir, 'csf')
sys.path.append(CSF_PATH)
    
from Table import message as msg

def verify_columns(reqcode, fileh, header_string):
    ''' (str, fileIO, str) -> list of str
    Test fileh validity against mandatory column rules
    '''
    # Variables
    reqcode = reqcode # possible values ('reqdetect' or 'reqdistmtrx')
    fileh = fileh
    header_string = [unicode(x,errors='ignore') for x in header_string]
    errors = []
    missing_columns = []
    header_length = len(header_string)
    
    # Column tests
    unqdetecid_tst = False
    datecollected_tst = False
    catalognumber_tst = False
    station_tst = False
    stn1_tst = False
    stn2_tst = False
    distance_m_tst = False
    real_distance_tst = False
    matrix_pair_tst = False
    
    # Column indexes
    unqdetecid_idx = -1
    datecollected_idx = -1
    catalognumber_idx = -1
    station_idx = -1
    stn1_idx = -1
    stn2_idx = -1
    distance_m_idx = -1
    real_distance_idx = -1

    index = 2 # Current Line number
    unqdetecids = {} # List of uniquiecids
    unqdetecids_dup = [] # Duplicate records
    invalid_dates = [] # Invalid Date fields
    missing_data = [] # Columns with missing data
    catalognumber_nulls = [] # Null values for catalognumber
    station_nulls = [] # Null values for station column
    stn1_nulls = [] # Null values for stn1 column
    stn2_nulls = [] # Null values for sta2 column
    distance_m_invalid = [] # Invalid Date format
    real_distance_invalid = [] # Invalid numeric values for real distance
    matrix_pairs = {} # Matrix pairs
    matrix_pairs_invalid = [] # Invalid matrix pairs
    row_length_invalid = False
    duplicate_headers = False
    
    # Test to see if mandatory columns are met, else return error
    if (reqcode == 'reqdetect'):
        if u'unqdetecid' in header_string:
            unqdetecid_tst = True
            unqdetecid_idx = header_string.index(u'unqdetecid')
        else:
            missing_columns.append('unqdetecid')
            
        if u'datecollected' in header_string:
            datecollected_tst = True
            datecollected_idx = header_string.index(u'datecollected')
        else:
            missing_columns.append('datecollected')
            
        if u'catalognumber' in header_string:
            catalognumber_tst = True
            catalognumber_idx = header_string.index(u'catalognumber')
        else:
            missing_columns.append('catalognumber')
            
        if u'station' in header_string:
            station_tst = True
            station_idx = header_string.index(u'station')
        else:
            missing_columns.append('station')
             
        if missing_columns:
            errors.append(msg('simple',105,2,param1='Detection', param2=os.path.basename(str(fileh))))
            for col in missing_columns:
                errors.append(col)
        
    elif(reqcode == 'reqdistmtrx'):
        if u'stn1' in header_string:
            stn1_tst = True
            stn1_idx = header_string.index(u'stn1')
        else:
            missing_columns.append('stn1')
            
        if u'stn2' in header_string:
            stn2_tst = True
            stn2_idx = header_string.index(u'stn2')
        else:
            missing_columns.append('stn2')
            
        if u'distance_m' in header_string:
            distance_m_tst = True
            distance_m_idx = header_string.index(u'distance_m')
        else:
            missing_columns.append('distance_m')
            
        if u'real_distance' in header_string:
            real_distance_tst = True
            real_distance_idx = header_string.index(u'real_distance')
        else:
            missing_columns.append('real_distance')
             
        if missing_columns:
            errors.append(msg('simple',105,2,param1='Distance matrix', param2=os.path.basename(str(fileh))))
            for col in missing_columns:
                errors.append(col)
        else:
            matrix_pair_tst = True
    else:
        #Invalid request code: '{reqcode}'
        errors.append(msg('simple',12,1,param1=reqcode))
    
    #Null in column headers
    if u'' in header_string:
        errors.append(msg('simple',120,1,param1=os.path.basename(str(fileh))))
    
    if len(set(header_string)) < len(header_string):
        errors.append(msg('simple',121,1,param1=os.path.basename(str(fileh))))
    
    #Return initial errors
    if errors:
        return errors
    
    # Read File & accumulate errors
    row = fileh.fileIO('reqread1',fromto=':list:')
    
    while row:
        # if row is larger or smaller than available column headers 
        row_length = len(row)
        if row_length != header_length and not row_length_invalid:
            row_length_invalid = True
        
        # unqdetecid (unique)
        if unqdetecid_tst:
            try:
                if unqdetecids.has_key(row[unqdetecid_idx]):  
                    unqdetecids_dup.append((row[unqdetecid_idx], index))
                else:
                    unqdetecids[row[unqdetecid_idx]] = index
            except:
                missing_data.append(index)
        
        # datecollected ('%Y-%m-%d %H:%M:%S')
        if datecollected_tst:
            try:
                try:
                    time.strptime(row[datecollected_idx], '%Y-%m-%d %H:%M:%S')
                except:
                    invalid_dates.append( (row[datecollected_idx], index))
            except:
                missing_data.append(index)
        
        # catalognumber (NOT NULL)
        if catalognumber_tst:
            try:
                if row[catalognumber_idx] == '':
                    catalognumber_nulls.append(index)
            except:
                missing_data.append(index)
        
        # station (NOT NULL)
        if station_tst:
            try:
                if row[station_idx] == '':
                    station_nulls.append(index)
            except:
                missing_data_.append(index)
        
        # stn1 (NOT NULL)
        if stn1_tst:
            try:
                if row[stn1_idx] == '':
                    stn1_nulls.append(index)
            except:
                missing_data.append(index)
                
        # stn2 (NOT NULL)
        if stn2_tst:
            try:
                if row[stn2_idx] == '':
                    stn2_nulls.append(index)
            except:
                missing_data.append(index)
        
        # distance_m (number)
        if distance_m_tst:
            try:
                if not is_number(row[distance_m_idx]):
                    distance_m_invalid.append(index)
            except:
                missing_data.append(index)
        
        # real_distance (NULL or number)
        if real_distance_tst:  
            try:
                if not row[real_distance_idx] == '':
                    if not is_number(row[real_distance_idx]):
                        real_distance_invalid.append(index)
            except:
                missing_data.append(index)
        
        if matrix_pair_tst:
            stn = ','.join(sorted([row[stn1_idx], row[stn2_idx]]))
            dis = [row[distance_m_idx], row[real_distance_idx], index]
            if matrix_pairs.has_key(stn):
                if not matrix_pairs[stn][:2] == dis[:2]:
                    matrix_pairs_invalid.append((stn, matrix_pairs[stn][2], index))
            else:
                matrix_pairs[stn] = dis
        
        # Read the next row and increment the row index
        row = fileh.fileIO('reqread1',fromto=':list:')
        index += 1
    
    #det_mandatory_columns = [u'unqdetecid', u'datecollected', u'catalognumber', u'station']
    #dismtx_mandatory_coulmns = [u'stn1',u'stn2',u'distance_m',u'real_distance']
    
    #Build error messages
    if row_length_invalid:
        errors.append(msg('simple',119,
                          1,param1=os.path.basename(str(fileh))))
    if unqdetecids_dup:
        errors.append(msg('simple',106,
                          2,param1=os.path.basename(str(fileh)),
                          param2='unqdetecids'))
        errors.append([x[1] for x in unqdetecids_dup])
    
    if invalid_dates:
        errors.append(msg('simple',107,
                          2,param1=os.path.basename(str(fileh)),
                          param2='datecollected'))
        errors.append([x[1] for x in invalid_dates])
    
    if catalognumber_nulls:
        errors.append(msg('simple',108,
                          2,param1=os.path.basename(str(fileh)),
                          param2='datecollected'))
        errors.append(catalognumber_nulls)
    
    if station_nulls:
        errors.append(msg('simple',108,
                          2,param1=os.path.basename(str(fileh)),
                          param2='station'))
        errors.append(station_nulls)
    
    if stn1_nulls:
        errors.append(msg('simple',108,
                          2,param1=os.path.basename(str(fileh)),
                          param2='stn1'))
        errors.append(stn1_nulls)
        
    if stn2_nulls:
        errors.append(msg('simple',108,
                          2,param1=os.path.basename(str(fileh)),
                          param2='stn2'))
        errors.append(stn1_nulls)
        
    if real_distance_invalid:
        errors.append(msg('simple',111,
                          2,param1=os.path.basename(str(fileh)),
                          param2='real_distance'))
        errors.append(real_distance_invalid)
        
    if distance_m_invalid:
        errors.append(msg('simple',110,
                          2,param1=os.path.basename(str(fileh)),
                          param2='distance_m'))
        errors.append(distance_m_invalid)
        
    if matrix_pairs_invalid:
        errors.append(msg('simple',109,
                          1,param1=os.path.basename(str(fileh))))
        station_pairs = ['stn:{0} rows:{1},{2}'.format(*x) for x in matrix_pairs_invalid]
        for pair in station_pairs:
            errors.append(pair)
    return errors

def is_number(s):
    '''(str) -> bool
    Return true if string is a number
    '''
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

# if __name__ == '__main__':
#     from file_io import fileIO
# 
#     data_directory = 'W:\\RStudio\\data\\'
#     detection_filename = 'sample_missing header.csv'
#     detection_filepath = os.path.join(data_directory, detection_filename) # (str) Set absolute path for detection file
#     detection_fileh = fileIO('reqopen', detection_filepath )
#     detection_file_header = detection_fileh.fileIO('reqread1',fromto=':list:')
#     print detection_file_header
#     # possible values ('reqdetect' or 'reqdistmtrx')
#      
#     errors = verify_columns(reqcode='reqdetect',fileh=detection_fileh, header_string=detection_file_header)
#     
# #     data_directory = 'W:\\RStudio\\data\\'
# #     detection_filename = 'nsbs_matched_detections_2013_distance_matrix_v00.csv'
# #     detection_filepath = os.path.join(data_directory, detection_filename) # (str) Set absolute path for detection file
# #     detection_fileh = fileIO('reqopen', detection_filepath )
# #     detection_file_header = detection_fileh.fileIO('reqread1',fromto=':list:')
# #     
# #     errors = verify_columns(reqcode='reqdistmtrx',file=detection_fileh, header_string=detection_file_header)
#     
#     for error in errors:
#         print error
    