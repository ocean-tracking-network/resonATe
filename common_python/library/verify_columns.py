import os
import sys
import re
import time 

from collections import Counter

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CSF_PATH = os.path.join(SCRIPT_PATH, os.pardir,os.pardir, 'csf')
sys.path.append(CSF_PATH)

import MessageDB as mdb
msgs = mdb.MessageDB()

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
    detec_rad1_tst = False
    detec_rad2_tst = False
    distance_m_tst = False
    real_distance_tst = False
    matrix_pair_tst = False
    startdate_tst = False
    enddate_tst = False
    longitude_tst = False
    latitude_tst = False
    
    # Column indexes
    unqdetecid_idx = -1
    datecollected_idx = -1
    catalognumber_idx = -1
    station_idx = -1
    stn1_idx = -1
    stn2_idx = -1
    distance_m_idx = -1
    real_distance_idx = -1
    detec_rad1_idx = -1
    detec_rad2_idx = -1
    startdate_idx = -1
    enddate_idx = -1
    latitude_idx = -1
    longitude_idx = -1

    index = 2 # Current Line number
    unqdetecids = {} # List of uniquiecids
    unqdetecids_dup = [] # Duplicate records
    invalid_dates = [] # Invalid Date fields
    invalid_startdates = []
    invalid_enddates = []
    missing_data = set() # Rows with missing data
    missing_data_columns = set() # Column names where there is data missing
    distance_m_invalid = [] # Invalid Date format
    detect_rad1_invalid = [] # Invalid detec_radius1
    detect_rad2_invalid = [] # Invalid detec_radius2
    real_distance_invalid = [] # Invalid numeric values for real distance
    matrix_pairs = {} # Matrix pairs
    matrix_pairs_invalid = [] # Invalid matrix pairs
    row_length_invalid = False
    duplicate_headers = False
    longitude_invalid = []
    latitude_invalid = []

    print_limit = 10 # The amount of invalid columns to print
    
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

        if u'longitude' in header_string:
            longitude_tst = True
            longitude_idx = header_string.index(u'longitude')

        if u'latitude' in header_string:
            latitude_tst = True
            latitude_idx = header_string.index(u'latitude')

        if missing_columns:
            errors.append(msgs.get_message(105,params=['Detection', os.path.basename(str(fileh))]))
            for col in missing_columns:
                errors.append(col)
                
    # Test Detection file with distance matrix creation enabled
    elif (reqcode == 'reqdetect_w_distmtrx'):
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

        if u'longitude' in header_string:
            longitude_tst = True
            longitude_idx = header_string.index(u'longitude')
        else:
            missing_columns.append('longitude')

        if u'latitude' in header_string:
            latitude_tst = True
            latitude_idx = header_string.index(u'latitude')
        else:
            missing_columns.append('latitude')

        if missing_columns:
            errors.append(msgs.get_message(105,params=['Detection', os.path.basename(str(fileh))]))
            # Add the column names to the error list
            errors.append(','.join(missing_columns))
            
            if all([x=='longitude' or x=='latitude' for x in missing_columns]):
                errors.append(msgs.get_message(123,params=[]))
    
    # Checks to run for distance matrix files 
    elif(reqcode == 'reqdistmtrx'):
        # Verify the column names exist
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
            
        if u'detec_radius1' in header_string:
            detec_rad1_tst = True
            detec_rad1_idx = header_string.index(u'detec_radius1')
        else:
            missing_columns.append('detec_radius1')
        
        if u'detec_radius2' in header_string:
            detec_rad2_tst = True
            detec_rad2_idx = header_string.index(u'detec_radius2')
        else:
            missing_columns.append('detec_radius2')
               
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
            errors.append(msgs.get_message(105, params=['Distance matrix', os.path.basename(str(fileh))]))
            for col in missing_columns:
                errors.append(col)
        else:
            matrix_pair_tst = True

    # Check the compressed files
    elif(reqcode ==  'reqcompressed'):
        if u'catalognumber' in header_string:
            catalognumber_tst = True
            catalognumber_idx = header_string.index(u'catalognumber')
        else:
            missing_columns.append('catalognumber')

        if u'seq_num' not in header_string:
            missing_columns.append('seq_num')

        if u'station' not in header_string:
            missing_columns.append('station')

        if u'startdate' in header_string:
            startdate_tst = True
            startdate_idx = header_string.index(u'startdate')
        else:
            missing_columns.append('startdate')

        if u'enddate' in header_string:
            enddate_tst = True
            enddate_idx = header_string.index(u'enddate')
        else:
            missing_columns.append('enddate')

        if u'startunqdetecid' not in header_string:
            missing_columns.append('startunqdetecid')

        if u'total_count' not in header_string:
            missing_columns.append('total_count')

        if missing_columns:
            errors.append(msgs.get_message(105, params=['Compressed Detections', os.path.basename(str(fileh))]))
            for col in missing_columns:
                errors.append(col)
        else:
            matrix_pair_tst = True

    # Checks to run for distance matrix files 
    elif(reqcode == 'reqrealdistmtrx'):
        # Verify the column names exist
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
            
        if u'detec_radius1' in header_string:
            detec_rad1_tst = True
            detec_rad1_idx = header_string.index(u'detec_radius1')
        else:
            missing_columns.append('detec_radius1')
        
        if u'detec_radius2' in header_string:
            detec_rad2_tst = True
            detec_rad2_idx = header_string.index(u'detec_radius2')
        else:
            missing_columns.append('detec_radius2')
            
        if u'real_distance' in header_string:
            real_distance_tst = True
            real_distance_idx = header_string.index(u'real_distance')
        else:
            missing_columns.append('real_distance')
             
        if missing_columns:
            errors.append(msgs.get_message(105, params=['Distance real', os.path.basename(str(fileh))]))
            for col in missing_columns:
                errors.append(col)
        else:
            matrix_pair_tst = True
    else:
        #Invalid request code: '{reqcode}'
        errors.append(msgs.get_message(12,params=[reqcode]))
    
    #Null in column headers
    if u'' in header_string:
        errors.append(msgs.get_message(120,params=[os.path.basename(str(fileh))]))
    
    # Duplicate in column headers
    duplicate_headers = [k for k,v in Counter(header_string).items() if v > 1 ]
    if duplicate_headers:
        errors.append(msgs.get_message(124,params=[','.join(duplicate_headers)]))
    
    # Return initial errors
    if errors:
        return errors
    
    # Read File & accumulate errors
    row = fileh.fileIO('reqread1', fromto=':list:')
    
    while row:
        # if row is larger or smaller than available column headers 
        row_length = len(row)
        if row_length != header_length and not row_length_invalid:
            row_length_invalid = True

        # enddate ('%Y-%m-%d %H:%M:%S')
        if enddate_tst:
            if row[enddate_idx]:
                try:
                    time.strptime(row[enddate_idx], '%Y-%m-%d %H:%M:%S')
                except:
                    invalid_enddates.append("{0}:'{1}'".format(index, row[enddate_idx]))
            else:
                missing_data.add(index)
                missing_data_columns.add('enddate')

        # startdate ('%Y-%m-%d %H:%M:%S')
        if startdate_tst:
            if row[startdate_idx]:
                try:
                    time.strptime(row[startdate_idx], '%Y-%m-%d %H:%M:%S')
                except:
                    invalid_startdates.append("{0}:'{1}'".format(index, row[startdate_idx]))
            else:
                missing_data.add(index)
                missing_data_columns.add('startdate')

        # unqdetecid (unique)
        if unqdetecid_tst:
            if row[unqdetecid_idx]:
                if unqdetecids.has_key(row[unqdetecid_idx]):
                    unqdetecids_dup.append("{0}:'{1}'".format(index, row[unqdetecid_idx]))
                else:
                    unqdetecids[row[unqdetecid_idx]] = index
            else:
                missing_data.add(index)
                missing_data_columns.add('unqdetecid')

        # datecollected ('%Y-%m-%d %H:%M:%S')
        if datecollected_tst:
            if row[datecollected_idx]:
                try:
                    time.strptime(row[datecollected_idx], '%Y-%m-%d %H:%M:%S')
                except:
                    invalid_dates.append("{0}:'{1}'".format(index, row[datecollected_idx]))
            else:
                missing_data.add(index)
                missing_data_columns.add('datecollected')
        
        # catalognumber (NOT NULL)
        if catalognumber_tst:
            if row[catalognumber_idx] == '':
                missing_data.add(index)
                missing_data_columns.add('catalognumber')
        
        # station (NOT NULL)
        if station_tst:
            if row[station_idx] == '':
                missing_data.add(index)
                missing_data_columns.add('station')
        
        # stn1 (NOT NULL)
        if stn1_tst:
            if row[stn1_idx] == '':
                missing_data.add(index)
                missing_data_columns.add('stn1')
                
        # stn2 (NOT NULL)
        if stn2_tst:
            if row[stn2_idx] == '':
                missing_data.add(index)
                missing_data_columns.add('stn2')
        
        # distance_m (number)
        if distance_m_tst:
            try:
                if not is_number(row[distance_m_idx]):
                    distance_m_invalid.append(index)
            except:
                missing_data.add(index)
        
        # detec_radius1 (number)
        if detec_rad1_tst:
            try:
                if (not row[detec_rad1_idx] == '') & (not is_number(row[detec_rad1_idx])):
                    detect_rad1_invalid.append(index)
            except:
                missing_data.add(index)
                
        # detec_radius2 (number)
        if detec_rad2_tst:
            try:
                if (not row[detec_rad2_idx] == '') & (not is_number(row[detec_rad2_idx])):
                    detect_rad2_invalid.append(index)
            except:
                missing_data.add(index)
                
        # real_distance (NULL or number)
        if real_distance_tst:  
            if not row[real_distance_idx] == '':
                if not is_number(row[real_distance_idx]):
                    real_distance_invalid.append(index)

        if longitude_tst:
            if row[longitude_idx] == '':
                missing_data.add(index)
                missing_data_columns.add('longitude')
            else:
                if not is_number(row[longitude_idx]):
                    longitude_invalid.append(index)

        if latitude_tst:
            if row[latitude_idx] == '':
                missing_data.add(index)
                missing_data_columns.add('latitude')
            else:
                if not is_number(row[latitude_idx]):
                    latitude_invalid.append(index)

        if matrix_pair_tst:
            stn = ','.join(sorted([row[stn1_idx], row[stn2_idx]]))
            dis = [row[distance_m_idx], row[real_distance_idx], index]
            if matrix_pairs.has_key(stn):
                if not matrix_pairs[stn][:2] == dis[:2]:
                    matrix_pairs_invalid.append((stn, matrix_pairs[stn][2], index))
            else:
                matrix_pairs[stn] = dis
        
        # Read the next row and increment the row index
        row = fileh.fileIO('reqread1', fromto=':list:')
        index += 1
    
    #det_mandatory_columns = [u'unqdetecid', u'datecollected', u'catalognumber', u'station']
    #dismtx_mandatory_coulmns = [u'stn1',u'stn2',u'distance_m',u'real_distance']
    
    #Build error messages
    if row_length_invalid:
        errors.append(msgs.get_message(119,
                    params=[os.path.basename(str(fileh))]))
    if unqdetecids_dup:
        errors.append(msgs.get_message(106,
                    params=[os.path.basename(str(fileh)), 'unqdetecids']))

        errors.append(make_value_list(unqdetecids_dup, print_limit))
    
    if invalid_dates:
        errors.append(msgs.get_message(107,
                    params=[os.path.basename(str(fileh)), 'datecollected']))
        errors.append(make_value_list(invalid_dates, print_limit))

    if invalid_startdates:
        errors.append(msgs.get_message(107,
                    params=[os.path.basename(str(fileh)), 'startdate']))
        errors.append(make_value_list(invalid_startdates, print_limit))

    if longitude_invalid:
        errors.append(msgs.get_message(110,
                    params=[os.path.basename(str(fileh)), 'longitude']))
        errors.append(make_value_list(longitude_invalid, print_limit))

    if latitude_invalid:
        errors.append(msgs.get_message(110,
                    params=[os.path.basename(str(fileh)), 'latitude']))
        errors.append(make_value_list(latitude_invalid, print_limit))

    if invalid_enddates:
        errors.append(msgs.get_message(107,
                    params=[os.path.basename(str(fileh)), 'enddate']))
        errors.append(make_value_list(invalid_enddates, print_limit))
        
    if real_distance_invalid:
        errors.append(msgs.get_message(111,
                    params=[os.path.basename(str(fileh)), 'real_distance']))
        errors.append(make_value_list(real_distance_invalid, print_limit))
        
    if distance_m_invalid:
        errors.append(msgs.get_message(110,
                    params=[os.path.basename(str(fileh)), 'distance_m']))
        errors.append(make_value_list(distance_m_invalid, print_limit))
    
    if detect_rad1_invalid:
        errors.append(msgs.get_message(111,
                    params=[os.path.basename(str(fileh)), 'detec_radius1']))
        errors.append(make_value_list(detect_rad1_invalid, print_limit))
        
    if detect_rad2_invalid:
        errors.append(msgs.get_message(111,
                    params=[os.path.basename(str(fileh)), 'detec_radius2']))
        errors.append(make_value_list(detect_rad2_invalid, print_limit))
        
    if matrix_pairs_invalid:
        errors.append(msgs.get_message(109,
                    params=[os.path.basename(str(fileh))]))
        station_pairs = ['stn:{0} rows:{1},{2}'.format(*x) for x in matrix_pairs_invalid]
        errors.append(make_value_list(station_pairs, print_limit))

    if missing_data:
        errors.append(msgs.get_message(212,
                    params=[os.path.basename(str(fileh)), ','.join(missing_data_columns)]))
        errors.append(make_value_list(missing_data, print_limit))
    return errors

def make_value_list(arr, limit = 10):
    '''Create a printable list of column errors based on a limit'''
    # Build a new pritnable list not exceeding the limit value
    value_list = [(str(x) if (i%5 != 0 or i == 0) else '\n'+str(x)) for i, x in enumerate(arr) if i <= limit]

    if len(value_list) > limit:
            value_list[limit] = '...\n' + msgs.get_message(211, params=[len(arr) - limit])

    return ','.join(value_list)

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
