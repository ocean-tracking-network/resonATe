from . import pg_connection as pg

def putFile(reqcode, objfrom, objto):
    '''(str, str, str) -> int
    Retrieves a object from the database and saves it to the filesystem
    Returns the record count of the requested object or -1 on error
    '''
    
    reqcode = reqcode
    objfrom = objfrom
    objto = objto
    count = 0
    
    # Create Database Connection
    conn, cur = pg.createConnection() 
    
    if reqcode == 'reqtabcsv':
        #File handle
        fh = open(objto, 'wb')
        
        #Retrieve record count
        query_count = "SELECT count(*) as record_count FROM {0}".format(objfrom)
        cur.execute(query_count)
        count = cur.fetchone()['record_count'] # Get value of record count
        
        #Export Data
        query_copy = "COPY (SELECT * FROM {0}) TO STDOUT WITH CSV HEADER QUOTE AS \'\"\' ;".format(objfrom)
        cur.copy_expert(query_copy, fh)
        fh.close()
        
        #Close the connection
        cur.close()
        conn.close()
        return count
    else:
        # Output message: Invalid reqcode
        print msg('simple',12,1,param1=reqcode)
        return -1