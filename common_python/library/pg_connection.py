import psycopg2
import psycopg2.extras
import os

def createConnection(dic=None):
    '''(bool)(optional) -> (psycopg2.connection, psycopg2.cursor)
    
    Connect to local postgreSQL database 
    
    '''
    
    # Windows debugging, change address if os.name = 'nt'
    if os.name == 'nt':
        conn = psycopg2.connect('''host     = 192.168.56.101
                                   port     = 5432 
                                   dbname   = postgres 
                                   user     = postgres 
                                   password = otn123''' ) # Connection
    else:
        conn = psycopg2.connect('''host     = 127.0.0.1
                                   port     = 5432 
                                   dbname   = postgres 
                                   user     = postgres 
                                   password = otn123''' ) # Connection
    if dict:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # DictCursor    
    else:  
        cur = conn.cursor() # Cursor
    
    return conn, cur
    