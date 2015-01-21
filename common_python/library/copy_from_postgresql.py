from . import pg_connection as pg

def copyTableStructure(source_table, dest_table, drop=False):
    conn, cur = pg.createConnection()

    if drop:
        print 'Dropping existing table {0}'.format(dest_table)
        cur.execute("DROP TABLE IF EXISTS {0}".format(dest_table))
    cur.execute("CREATE TABLE {0} (LIKE {1})".format(dest_table, source_table))
    conn.commit()
    cur.close()
    conn.close()
    return True

def ExportTable( table_name, file_name ):
    #Create Database Connection
    conn, cur = pg.createConnection() 
    
    #File handle
    fh = open(file_name, 'wb')
    
    #Export Data
    cur.copy_expert("COPY (SELECT * FROM {0}) TO STDOUT WITH CSV HEADER QUOTE AS \'\"\' ;".format(table_name), fh)
    fh.close()
    
    #Close the connection
    cur.close()
    conn.close()
    
    return True

def ReturnDuplicates( table_name, unique_column ):
    #Create Database Connection
    conn, cur = pg.createConnection() 
    
    cur.execute("""DROP TABLE IF EXISTS public.duplications;""")
    conn.commit()
    
    cur.execute("""CREATE TABLE public.duplications
            (
              uniquecid character varying
            );""")
    conn.commit()
    
    cur.execute("""INSERT INTO public.duplications
        select {0} from (
          SELECT {0},
          ROW_NUMBER() OVER(PARTITION BY {0} ORDER BY {0} asc) AS Row
          FROM public.{1}
        ) dups
        where 
        dups.Row > 1""".format(unique_column, table_name))
    conn.commit()
    
    cur.close()
    conn.close()
    
    return True