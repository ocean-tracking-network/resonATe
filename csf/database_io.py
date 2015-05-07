import psycopg2
import psycopg2.extras
import os
import sys
import codecs
import ConfigParser

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )

sys.path.append( SCRIPT_PATH )
import MessageDB as mdb
msgs = mdb.MessageDB()

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
            print msgs.get_message(12,params=[reqcode])

    def databaseIO(self, reqcode, table=None, file=None):
        '''(databaseIO, str, str, str) -> NoneType
        Run databseIO functions based on reqcode
        '''
        if reqcode == 'reqconn':
            # database connection
            self.connect()
            
        elif reqcode == 'reqdisconn':
            # database disconnection
            self.disconnect()
            
        elif reqcode == 'reqlisttables':
            # list deletable tables in the public schema
            tables = self.list_tables()
            return tables
        
        elif reqcode == 'reqcleanup':
            # remove tables in the public schema
            
            # Get table list
            tables = self.list_tables()
            # Combine schema and table columns
            tables = ['{0}.\"{1}\"'.format(*row) for row in tables]
            
            # If tables array is not null, execute the cleanup operation
            if tables:
                self.cleanup_tables(tables)
            else:
                # Output: 'Nothing to cleanup from database.'
                print msgs.get_message(51)
                
        else:
            # Output: Invalid request code 'reqcode'
            print msgs.get_message(12, params=[reqcode])
      
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
        query = 'VACUUM FULL;'
        self.cur.execute( query )
        self.conn.commit()
        self.conn.set_isolation_level(old_isolation_level)
        
        # Output 'The following x tables have been dropped from the database'
        print msgs.get_message(50, params=[len(tables)])
        print '\n'.join(tables)
        
    def list_tables(self):
        '''(databaseIO) -> list of str
        List the tables in the public schema
        '''

        # Load external SQL script
        table_list_sql = codecs.open(os.path.join(SCRIPT_PATH, 'list_public_tables.sql'),
                                     'r',
                                     'utf-8')
        
        # Execute and fetch the results
        self.cur.execute(table_list_sql.read())
        
        return self.cur.fetchall()
        
    def connect(self):
        '''(databaseIO) -> NoneType
        Connect to the database
        
        Return: True if connection is successful, False if not
        '''
        # Load sandbox database configuration from db.cfg file
        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(SCRIPT_PATH, 'db.cfg'))


        host = config.get('Database', 'host')
        port = config.getint('Database', 'port')
        dbname = config.get('Database', 'dbname')
        user = config.get('Database', 'user')
        password = config.get('Database', 'password')

        # Create connection object
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