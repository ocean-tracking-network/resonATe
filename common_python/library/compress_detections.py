import os
import sys

from . import pg_connection as pg

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH, os.pardir, os.pardir, 'csf')

sys.path.append(CSF_PATH)

from Table import message as msg
from table_maintinance import table_maintinance

def compress_detections():
    '''
    Creates the compression table in the database
    '''
    #test if table mv_anm_compressed exists and drop if it does. Use CSF
    #Connect to the database
    db = table_maintinance('reqconn')
    
    mv_anm_compressed_exists = db.table_maintinance(reqcode='reqexist', tablename='mv_anm_compressed')
    if mv_anm_compressed_exists:
        db.table_maintinance(reqcode='reqdrop', tablename='mv_anm_compressed')
    
    #create table mv_anm_compressed.See Appendix A for SQL
    db.table_maintinance(reqcode='reqcreate', tablename='mv_anm_compressed')
    
    #create or replace function f_det_compressed(). See Appendix B for SQL
    db.table_maintinance(reqcode='reqcreate', tablename='f_det_compressed')
    
    #Close the table_maintinace module
    db.table_maintinance('reqdisconn')
    
    #Create new database connection for 
    conn, cur = pg.createConnection() 
    
    #Execute SQL statement 'select f_det_compressed();'
    query = 'select f_det_compressed();'
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

