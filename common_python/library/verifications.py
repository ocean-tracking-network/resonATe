import re
import os
import csv

from . import pg_connection as pg

def Filename( filename ):
    ''' (str) -> bool
    
    Return true if the filename value is correct for a csv.
    
    '''
    inv_filename_re = re.compile('^[\w,\s]+\.csv$') #RE: Check for valid filename characters
    if not inv_filename_re.search( filename ):
        return False
    if filename:
        return True
    
def FileVersionID( filename ):
    ''' (str) -> str
        
    Return the version string if the version_id value is in the filename.
    Return False if the version_id is not in the filename.
    
    '''
    file_version_id_re = re.compile('^_[v]+[0-9]{2}$') #RE: Check for version_id pattern
    filename_slice = filename[-8:-4].lower() #slice (filename end without file extension)
    if file_version_id_re.match( filename_slice ):
        return filename_slice[2:] #return numerical version_id
    else:
        return False

def VersionID( version_id ):
    ''' (str) -> bool
    
    Return True if the version_id is valid. Return False of the supplied version_id doesn't match the pattern
    '''
    version_id_re = re.compile('^[0-9]{1,2}$') #RE: Check if the version_id string between 0 and 99?
    if version_id_re.search( version_id ):
        return version_id
    else:
        return False
    
def TableExists( tablename ):
    '''(str) -> bool
    
    Return True if a table exists, False if not.
    
    '''
    #connect to local postgre 
    conn, cur = pg.createConnection()
    
    #search for table in the public schema
    cur.execute('''SELECT EXISTS (SELECT * FROM information_schema.tables 
                                    WHERE table_schema = 'public' 
                                    AND table_name = '{}');'''.format( tablename ))
    table_exists = cur.fetchone()[0] #get result
    
    #close postgresql connection
    cur.close()
    conn.close()
    
    return table_exists

def ColumnCount( tablename ):
    ''' (str) -> int
    
    Get the number of columns of a table
    
    '''
    #connect to local postgre 
    conn, cur = pg.createConnection()
    
    cur.execute('''SELECT count(*) FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = '{}';'''.format( tablename ))
    
    column_count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return column_count
    
def FileCount( filename, header=False ):
    ''' (file, bool) -> int
    
    Returns the number of lines in a file
    
    '''
    num_lines = sum(1 for line in open(filename)) 
    if header: 
        num_lines -= 1
     
    return num_lines

def tableDifference( table_1, table_2 ):
    # Return the difference between two table counts
    conn, cur = pg.createConnection() 
    
    sql = '''
    SELECT (SELECT count(*) FROM public.{0}) - (SELECT count(*) 
    FROM 
    public.{1}) 
    '''.format(table_1, table_2)

    #Execute SQL Script
    cur.execute(sql)
    table_count = cur.fetchone()[0] #get result
    
    #Close postgresql connection
    cur.close()
    conn.close()
    return table_count
    
def TableCount( tablename ):
    ''' (str) -> int
    
    Return the count of records in a database table
    
    '''
    #connect to local postgresql
    conn, cur = pg.createConnection()
    
    #search for table in the public schema
    cur.execute('''SELECT count(*) FROM public.{0};'''.format( tablename ))
    table_count = cur.fetchone()[0] #get result
    
    #close postgresql connection
    cur.close()
    conn.close()
    
    return table_count

def MandatoryColumns( csv_headers, mandatory_columns ):
    ''' (list of str, list or str) -> list of str
    
    Return a list of missing column_names from a given dataframe
     '''
    #Convert input headers to utf-8
    csv_headers = [unicode(x,errors='ignore') for x in csv_headers]
    
    #Check if mandatory columns exists within the CSV file
    missing_columns = []
    for mandatory_header in mandatory_columns:
        if mandatory_header not in csv_headers:
            missing_columns.append(mandatory_header)

    #Return the list of missing columns
    return missing_columns

def FileExists( filepath ):
    #Does the supplied file exists
    if os.path.isfile( filepath ):
        return True
    return False

def FileHeaders( filename ):
    with open(filename, 'rU') as csvfile:
        dialect = 'excel'
        reader = csv.reader(csvfile, dialect)
        
        try:
            return reader.next()
        except:
            return ''

def CheckDuplicateHeader( column_headers ):
    '''(list of str) -> list of str
    
    Return the list of duplicate column names
    '''
    headers = column_headers
    
    #Create list of duplications
    dup = set([i for i in headers if headers.count(i)>1])
    return list(dup)