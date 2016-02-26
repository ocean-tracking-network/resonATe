import psycopg2
import psycopg2.extras
import os
import sys
import ConfigParser

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH =  os.path.abspath(os.path.join(SCRIPT_PATH,
                                         os.pardir,
                                         os.pardir,
                                         'csf'))

sys.path.append(CSF_PATH)

def createConnection():
    '''(bool)(optional) -> (psycopg2.connection, psycopg2.cursor)
    
    Connect to local postgreSQL database

    '''
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(CSF_PATH, 'db.cfg'))

    host = config.get('Database', 'host')
    port = config.getint('Database', 'port')
    dbname = config.get('Database', 'dbname')
    user = config.get('Database', 'user')
    password = config.get('Database', 'password')

    # Connect and create cursor object
    conn = psycopg2.connect(host=host,
                               port=port,
                               dbname=dbname,
                               user=user,
                               password=password) # Connection

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return conn, cur


def get_engine():
    from sqlalchemy import create_engine

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(CSF_PATH, 'db.cfg'))
    host = config.get('Database', 'host')
    port = str(config.getint('Database', 'port'))
    dbname = config.get('Database', 'dbname')
    user = config.get('Database', 'user')
    password = config.get('Database', 'password')

    db_engine_name = "postgresql://%s:%s@%s:%s/%s" %(user, password, host, port, dbname)

    engine = create_engine(db_engine_name)
    return engine


get_engine()