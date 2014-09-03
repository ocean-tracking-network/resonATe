import psycopg2
import psycopg2.extras
import sys
import os
import re

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )

sys.path.append( SCRIPT_PATH )
import MessageDB as mdb
msgs = mdb.MessageDB()

class table_maintenance():
    def __init__(self, reqcode='reqconn', tablename=None, filename=None):
        '''
        Initialize the table_maintenance class
        '''
        # Presistance connection variables
        self.conn = None
        self.cur = None
        
        # table_maintenance must always be created first with the reqconn command
        if reqcode == 'reqconn':
            self.table_maintenance(reqcode, tablename, filename)
        else:
            #Invalid request code: '{0}'
            print msgs.get_message(12,params=[reqcode])
        
    def table_maintenance(self, reqcode, tablename=None, filename=None):
        '''
        Main function used to process the reqcode
        '''
        reqcode = reqcode
        tablename = tablename
        
        if reqcode == 'reqcreate':
            self.create_table(tablename, filename)
                
        elif reqcode == 'reqexist':
            # Query to see if a table exists
            query = ''' SELECT * FROM information_schema.tables WHERE table_schema = 'public'
            AND table_name = %s;
            '''
            
            self.cur.execute(query, (tablename,))
            
            # If there is a result from the query, the table exists (True) else (False)
            result = self.cur.fetchone()
            if result:
                return True
            else:
                return False
                
        elif reqcode == 'reqdrop':
            # Drop a table 
            self.drop_table(tablename)
        
        elif reqcode == 'reqdropcscd':
            # Drop a table using the CASCADE mode
            self.drop_cascade(tablename)
            
        elif reqcode == 'reqload':
            # Load a table from a csv file
            self.load_data(tablename, filename)
        elif reqcode == 'reqconn':
            self.connect()
        elif reqcode == 'reqdisconn':
            self.disconnect()
        else:
            # inform user that an invaild request code was given
            print msgs.get_message(index=12, params=[reqcode])

    def create_table(self, tablename, filename):
        '''(table_maintenance, str) -> NoneType
        Creates the table as specified by the tablename var
        '''
        query = ''
        
        if tablename == 'mv_anm_detections' or tablename == 'distance_matrix':
            # filename variable is used for column_names, use re to sanitize the column_names
            column_names = filename
            column_names = [re.sub(r'\W+', '', col.replace(' ','_')).lower().strip('_') for col in column_names]
            
            # Construct MessageDB auto-creation
            query = '''
            CREATE TABLE public.{0} ({1})
            '''.format(tablename,
                       ','.join(['\"{0}\" character varying'.format(col) for col in column_names]))
            
        elif tablename == 'mv_anm_compressed':
            #Open and run external SQL
            query_file = open(os.path.join(SCRIPT_PATH,'create_tbl_mv_anm_compressed.sql'), 'rb')
            query = query_file.read()
            query_file.close()
        elif tablename == 'f_det_compressed':
            #Open and run external SQL
            query_file = open(os.path.join(SCRIPT_PATH,'create_fnc_f_det_compressed.sql'), 'rb')
            query = query_file.read()
            query_file.close()
        else:
            return msgs.get_message(index=102, params=[tablename])
        
        self.cur.execute(query)
        self.conn.commit()
        
    def drop_cascade(self, tablename):
        ''' (table_maintenance, str) -> NoneType
        DROP CASCADE a table
        
        '''
        query = 'DROP TABLE public.{0} CASCADE'.format(tablename)
        self.cur.execute(query)
        self.conn.commit()
        
    def drop_table(self, tablename):
        ''' (table_maintenance, str) -> NoneType
        DROP a table
        
        '''
        query = 'DROP TABLE public.{0}'.format(tablename)
        self.cur.execute(query)
        self.conn.commit()    
        
    def load_data(self, tablename, filename):
        '''(str,str)-> str
        Load data from filename into tablename
        '''
        
        #Load the csv file using copy_expert
        try:
            self.cur.copy_expert("""set client_encoding= '{2}'; 
                                    COPY {3} FROM STDIN WITH DELIMITER \'{0}\' 
                                    CSV HEADER QUOTE \'{1}\'""".format(',','\"','utf-8',tablename ), open(filename,'rb'))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print e
            return e
    
    def connect(self):
        '''(table_maintenance) -> NoneType
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
                                password=password)                             # Connection
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # Cursor 

    def disconnect(self):
        '''(table_maintenance) -> NoneType
        Disconnect from the database 
        '''
        self.cur.close()
        self.conn.close()