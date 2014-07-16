import os
import re
from Table import message as msgCSF
    
def get_version( filename ):
    ''' (str) -> (list of (int, str))
    Function to determines version id number from the filename 
    and returns the base file name 
    
    >>> get_version( 'a.csv' )
    (0, 'a')
    >>> get_version( 'sample_v01.csv' )
    (1, 'sample')
    >>> get_version( 'sample_v99.csv' )
    (99, 'sample')
    '''
    filename = filename
    version_id = 0
    filename_wo_ext = os.path.splitext(filename)[0] # filename with removed extension
    base_filename = filename_wo_ext # filename without extension and version_id ()
    
    file_version_id_re = re.compile('^_[vV]+[0-9]{2}$') #RE: Check for version_id pattern
    
    if file_version_id_re.match( filename_wo_ext[-4:] ):
        version_id =  int(filename_wo_ext[-2:]) #return numerical version_id
        base_filename = filename_wo_ext[:-4]
    
    return version_id, base_filename

def build_filename(reqcode, filename):
    ''' (str str) -> str
    
    Build the output filename based on the input filename
    
    Tests:
        >>> build_filename( 'invalid', 'invalid.csv' )
        'Invalid request code invalid'
        >>> build_filename( 'reqcompressed', 'test_normal_v01.csv' )
        'test_normal_compressed_detections_v01.csv'
        >>> build_filename( 'reqcompressed', 'test_without_vid.csv' )
        'test_without_vid_compressed_detections_v00.csv'
        >>> build_filename( 'reqinterval', 'test_interval_v02.csv')
        'test_interval_interval_data_v02.csv'
    '''
    
    reqcode = reqcode
    filename = filename
    version_id, base_filename = get_version( filename )
    fmt_version_id = str(version_id).rjust(2,'0')
    output_filename = ''
    
    if reqcode == 'reqcompressed':
        output_filename = '{0}_compressed_detections_v{1}.csv'.format(base_filename, fmt_version_id)
        return output_filename
    elif reqcode == 'reqinterval':
        output_filename = '{0}_interval_data_v{1}.csv'.format(base_filename, fmt_version_id)
        return output_filename
    else:
        # Output message for an invalid request code
        return msgCSF(requestCode='simple', index=12, 
               numbOfParameters=1, param1=reqcode)
        

if __name__ == '__main__':
    import doctest
    doctest.testmod()