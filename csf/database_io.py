import psycopg2
import psycopg2.extras
import os
import sys

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')

sys.path.append( CSF_PATH )
from MessageDB import message as msg

class databaseIO():
    def __init__(self, reqcode='reqconn', table=None, file=None):
        ''' Set the local variables and then call the databaseIO function '''
        
        self.conn = None # Connection
        self.cur = None  # Cursor
        
        # databaseIO must always be created first with the reqconnect command
        if reqcode == 'reqconn':
            self.databaseIO(reqcode, table, file)
        else:
            #Invalid request code: '{0}'
            print msg('simple',12,1,param1=reqcode)

    def databaseIO(self, reqcode, table=None, file=None):
        '''(databaseIO, str, str, str) -> NoneType
        Run databseIO functions based on reqcode
        '''
        if reqcode == 'reqconn':
            self.connect()
            
        elif reqcode == 'reqdisconn':
            self.disconnect()
            
        elif reqcode == 'reqlisttables':
            tables = self.list_tables()
            return tables
        
        elif reqcode == 'reqcleanup':
            tables = self.list_tables()
            tables = ['{0}.{1}'.format(*row) for row in tables]
            
            if tables:
                self.cleanup_tables(tables)
            else:
                # Output 'Nothing to cleanup from database.'
                print msg('simple',51,0)
                
        else:
            # Output message for invalid reqcode
            print msg('simple',12,1,param1=reqcode)
      
    def cleanup_tables(self, tables):
        '''(databaseIO, (list of str)) -> NoneType
        Deletes all the tables in a given list
        
        '''
        tables = tables # List of tables to remove
        
        # Create DROP TABLE statements 
        query = '\n'.join(["DROP TABLE IF EXISTS {0} CASCADE;".format(tbl) for tbl in tables])
        self.cur.execute( query )
        self.conn.commit()
        
        # Run VACUUM function 
        old_isolation_level = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        query = 'VACUUM FULL'
        self.cur.execute( query )
        self.conn.commit()
        self.conn.set_isolation_level(old_isolation_level)
        
        # Print output messages
        print msg('simple',50,1,param1=len(tables))
        print '\n'.join(tables)
        
    def list_tables(self):
        '''(databaseIO) -> list of str
        List tables
        '''
        
        query = '''SELECT table_schema, table_name FROM information_schema.tables
                WHERE table_schema  in ('public')
                AND table_name not in ( 'geography_columns','geometry_columns',    
                'raster_columns','raster_overviews','spatial_ref_sys')'''
        
        self.cur.execute(query)
        
        return self.cur.fetchall()
        
    def connect(self):
        '''(databaseIO) -> NoneType
        Connect to the database
        
        '''
        if os.name == 'nt':
            host = '192.168.56.101'
        else:
            host = '127.0.0.1'
        port = 5432
        dbname = 'postgres'
        user = 'postgres'
        password = 'otn123' 
        
        self.conn = psycopg2.connect(host=host, port=port, 
                                dbname=dbname,user=user, 
                                password=password)               # Connection
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # Cursor 

    def disconnect(self):
        '''(databaseIO) -> NoneType
        Disconnect from the database 
        '''
        self.cur.close()
        self.conn.close()
    