import psycopg2
import psycopg2.extras
import sys
import shapely

from . import pg_connection as pg

def createMatrix( detection_tbl, matrix_tbl ):
    #Create Database Connection
    conn, cur = pg.createConnection() 
    
    #SQL for creating the station matrix table
    cur.execute('''
        DROP TABLE IF EXISTS public.{0};
        CREATE TABLE public.{0} (
        stn1 varchar,
        stn2 varchar,
        avg_lat1 numeric,
        avg_lat2 numeric,
        avg_long1 numeric,
        avg_long2 numeric,
        distance_m numeric,
        real_distance numeric
        );
        '''.format( matrix_tbl ))
    conn.commit()
     
    #SQL to populate the station matrix file
    try:
        cur.execute('''INSERT INTO {1} (
            select *,
            coalesce(round(ST_Distance_Spheroid(st_makepoint(avg_long1, avg_lat1,4326)
            ,st_makepoint(avg_long2, avg_lat2,4326),'SPHEROID["WGS 84",6378137,298.257223563]')::numeric,0)::text)::numeric as distance_m
            ,NULL as real_distance from (
            select stn1,stn2, round(avg(lat1::numeric),5)::numeric as avg_lat1,round(avg(lat2::numeric),5)::numeric as avg_lat2 ,round(avg(long1::numeric),5)::numeric as avg_long1,round(avg(long2::numeric),5)::numeric as avg_long2  from (
            select  fst.station as stn1,snd.station as stn2,
            fst.latitude as lat1, snd.latitude as lat2,
            fst.longitude as long1, snd.longitude as long2
             from (select row_number()over( order by catalognumber, datecollected) as row_num
                     ,* from  {0}) fst
            join (select row_number()over( order by catalognumber, datecollected) as row_num
                     ,* from  {0}) snd
              on fst.row_num = snd.row_num -1
              and fst.catalognumber = snd.catalognumber
             and fst.station != snd.station
            ) foo group by 1,2
            )calc
            order by 1,2);
            '''.format(detection_tbl, matrix_tbl))
        conn.commit()
    except Exception as e:
        if hasattr(e, 'pgcode'):
            if e.pgcode == '22P02':
                #Invalid numeric type found in either longitude or latitude columns
                print "Error: Invalid numeric type in either the latitude or longitude columns\nFix the input file and rerun this process." 
            return False
        else:
            print e
    
    #Remove duplicate distance matrix pairs
    
    sql = '''
        DELETE FROM public.{0}
        
        WHERE ( stn1,stn2 ) not IN
       (
            SELECT
              stn1
            , stn2
        
            FROM 
            (
                SELECT
                  DISTINCT ON ( array_to_string ( f_ARRAY_SORT ( ARRAY[stn1,stn2]),',' ) ) stn1
                , stn2
                , avg_lat1
                , avg_lat2
                , avg_long1
                , avg_long2
                , distance_m
                , real_distance
        
                FROM public.{0}
            )
            foo
        )
    '''.format(matrix_tbl)
    try:
        #Execute SQL Script
        cur.execute(sql)
        conn.commit()
        
        #Close postgresql connection
        cur.close()
        conn.close()
        return True
    except:
        return False

def createSuspect( detection_tbl, suspect_tbl, time_interval):
    #Create Database Connection
    conn, cur = pg.createConnection()
    
    #Create table to hold detection summary
    cur.execute('''DROP TABLE IF EXISTS public.{0};
        CREATE TABLE public.{0} (
        row_num bigint,
        catalognumber character varying,
        detecid1  character varying,
        suspect_detection  character varying,
        detecid3  character varying,
        stn1  character varying,
        stn2  character varying,
        stn3 character varying,
        frst_detec timestamp without time zone,
        scnd_detect timestamp without time zone,
        thrd_detect timestamp without time zone,
        prev_interval interval,
        next_interval interval,
        input_interval character varying
        );
        '''.format( suspect_tbl ))
    conn.commit()
     
    #Begin detection processing routine
    print 'Processing detection summary on table {0} using the time interval: {1} minute(s)'.format(detection_tbl, time_interval)
     
    #Write to the detection summary table
    cur.execute('''
        INSERT INTO public.{0} (select * from (
        select fst.row_num,fst.catalognumber,fst.unqdetecid as detecid1 ,snd.unqdetecid as suspect_detection
        ,trd.unqdetecid as detecid3
        ,fst.station as stn1,snd.station as stn2,trd.station as stn3
        ,fst.datecollected as frst_detec ,snd.datecollected as scnd_detect,trd.datecollected as thrd_detect
        , snd.datecollected - fst.datecollected as prev_interval
        , trd.datecollected - snd.datecollected as next_interval,
        'GT '||{2}||' minutes'
         from (select row_number()over( order by catalognumber,datecollected) as row_num
          ,* from  public.{1} ) fst
         -- 201407 change from join to a left join to pick up single detections
        -- 201407 single release records will be eliminated in the  at the end
 left join (select row_number()over( order by catalognumber,datecollected) as
            row_num  -- 201407 change to left join
           ,* from  public.{1}) snd
          on fst.row_num = snd.row_num -1
          and fst.catalognumber = snd.catalognumber
        -- this is a left join as we want all cases where there are at lease two detections to show up. Three detections is not
        -- necessary.
        left join (select row_number()over( order by catalognumber,datecollected) as row_num
                 ,* from  public.{1}) trd
          on fst.row_num = trd.row_num -2
          and fst.catalognumber = trd.catalognumber
        ) foo
         where (prev_interval >  interval'{2} minute' and next_interval >
                  interval'{2} minute' )
         or (prev_interval > interval'{2} minute' and next_interval is null ) -- case where the last detec is isolated
         or (suspect_detection is null and detecid3 is null and detecid1 not like
               '%release'
         and  (catalognumber,frst_detec::text )
         not in (
              select catalognumber,max_date from (
                  select catalognumber,max(datecollected)::text as max_date, count(*) as cnt
                  from public.{1} group by 1)
                  foo where cnt > 1)
               ) --201407 flag single detections unless release
        order by catalognumber, frst_detec
        );
'''.format(suspect_tbl,detection_tbl, time_interval))
    conn.commit()
    return True

def loadToPostgre( table_name, filename):
    data_loaded = False
    
    # Create connection
    conn, cur = pg.createConnection()
    
    # Try to load the file directly
    try:
        print "Loading records into {0}, Please wait...".format( table_name ) 
        cur.copy_expert("""set client_encoding= '{2}'; 
                                COPY {3} FROM STDIN WITH DELIMITER \'{0}\' 
                                CSV HEADER QUOTE \'{1}\'""".format(',','\"','utf-8',table_name ), open(filename,'rb'))
        conn.commit()
        data_loaded = True
    except Exception as e:
        conn.rollback()
        if hasattr(e, 'pgcode'):
            if e.pgcode == '22021':
                print "Error: Please use conversion function on your input file \'{0}\'.".format(filename)
            elif e.pgcode == '22P04':
                # Extract line number
                print "Error: Missing/Extra data, please fix input file and rerun load_detections()."
                print e
            else: 
                print e
        else:
            print e
        data_loaded = False
        
    # Close postgresql connection
    cur.close()
    conn.close()
    
    return data_loaded

def createGeometryColumns(table_name):

    conn, cur = pg.createConnection()
    cur.execute("select column_name from information_schema.columns \
                    WHERE table_name = '%s' and data_type = 'character varying'" % (table_name))

    text_cols = cur.fetchall()
    geo_cols = []
    srid = 4326 # this doesn't get included in wkb/wkt. No way to read it out of the geom usually.
    # TODO: find the appropriate SRID given the geometry object.

    for col_name in text_cols:
        check_q = "select %s from %s" % (col_name[0], table_name)
        cur.execute(check_q)
        col_contents = cur.fetchall()
        try: # try binary.
            populated_column = False
            for item in col_contents:
                if item[0]:
                    geom = shapely.wkb.loads(item[0], True)
                    populated_column = True
            if populated_column:
                geo_cols.append([col_name[0], 'WKB', geom.geom_type])
        except:
            try: # try WKT
                populated_column = False
                for item in col_contents:
                    if item[0]:
                        geom = shapely.wkt.loads(item[0])
                        populated_column = True
                if populated_column:
                    geo_cols.append([col_name[0], 'Text', geom.geom_type])
            except:
                continue
            continue

    for col in geo_cols:
        # Update the geometry columns here.
        # Create a column with the same name as the source column with the prefix geom_
        geom_sql = "select AddGeometryColumn('public', '{0}', '{1}', {2}, '{3}', 2, false)\
                    ".format(table_name, 'geom_%s' % col[0], srid, col[2].upper())
        gis_func_call = "ST_GeomFromE%s" % col[1]
        if col[1] == 'WKB':
            col_decode = "decode(%s, 'hex')" % col[0] # Binary needs to be decoded from ASCII representing hex.
        else:
            col_decode = col[0]
        geom_pop_sql = "update {0} set {1}={2}({3})".format(table_name,
                                                            'geom_%s' % col[0],
                                                            gis_func_call,
                                                            col_decode)
        #print geom_sql
        print 'Creating geometry column for %s, identified as %s' % (col[0], col[1])
        cur.execute(geom_sql)
        conn.commit()
        #print geom_pop_sql
        print 'Populating geometry column with %s' % gis_func_call
        cur.execute(geom_pop_sql)
        conn.commit()

    # Determine whether there is a latitude and longitude pair of columns from which to make a Geometry POINT object
    if ['longitude'] in text_cols and ['latitude'] in text_cols:
        createLatLonGeom = True
        print 'LatLon detected, creating a Point object from latitude/longitude'

    conn.close()
    return geo_cols

def createTable( table_name, csv_headers, drop=False ):
    #Create Database Connection
    conn, cur = pg.createConnection() 
    if drop:
            sql = "DROP TABLE IF EXISTS {0}; CREATE TABLE {0}({1});".format( table_name, 
                   ','.join(['\"{0}\" {1}'.format(head, 
                   'timestamp' if head == 'datecollected' else 'varchar') for head in csv_headers]))
    else:
        sql = "CREATE TABLE {0}({1});".format( table_name, 
                    ','.join(['\"{0}\" {1}'.format(head, 
                    'timestamp' if head == 'datecollected' else 'varchar') for head in csv_headers]))
    try:
        cur.execute(sql)
        conn.commit()

        #Close postgresql connection
        cur.close()
        conn.close()
        return True
    except Exception as e:
        if hasattr(e, 'pgcode'):
            if e.pgcode == '22021':
                print "Error: Please use conversion function on your input file."
        else:
            print e
        return False
    
def removeTable( table_name ):
    #Create Database Connection
    conn, cur = pg.createConnection() 
    sql = "DROP TABLE public.{0};".format( table_name )
    
    try:
        #Execute SQL Script
        cur.execute(sql)
        conn.commit()
        
        #Close postgresql connection
        cur.close()
        conn.close()
        return True
    except:
        return False

def removeNullRows( table_name, unique_column ):
    '''
    Removes rows based on unique_column either being a NULL or a empty string
    '''  
    #Create Database Connection
    conn, cur = pg.createConnection() 
    
    sql = '''
    DELETE FROM {0} WHERE {1} is NULL OR {1} = '';
    '''.format(table_name, unique_column)
    
    cur.execute(sql)
    conn.commit()
  
def createArraySort():
    conn, cur = pg.createConnection()
    
    sql = '''
    DROP FUNCTION IF EXISTS f_array_sort(anyarray);
    CREATE FUNCTION
    f_array_sort(
        array_vals_to_sort anyarray
    )
    RETURNS TABLE (
        sorted_array anyarray
    )
    AS $BODY$
        BEGIN
            RETURN QUERY SELECT
                ARRAY_AGG(val) AS sorted_array
            FROM
                (
                    SELECT
                        UNNEST(array_vals_to_sort) AS val
                    ORDER BY
                        val
                ) AS sorted_vals
            ;
        END;
    $BODY$
    LANGUAGE plpgsql;
    '''      
    try:
        #Execute SQL Script
        cur.execute(sql)
        conn.commit()
        
        #Close postgresql connection
        cur.close()
        conn.close()
        return True
    except:
        return False
         
def removeSuspect( detection_tbl, suspect_tbl, output_tbl):
    #Create Database Connection
    conn, cur = pg.createConnection() 
    
    sql = '''
        INSERT INTO public.{2}
        SELECT
          det.*
        
        FROM public.{0} det
        
        LEFT JOIN public.{1} sus
         ON unqdetecid=suspect_detection
        
        WHERE suspect_detection IS NULL

    '''.format(detection_tbl, suspect_tbl, output_tbl)
    try:
        #Execute SQL Script
        cur.execute(sql)
        conn.commit()
        
        #Close postgresql connection
        cur.close()
        conn.close()
        return True
    except:
        return False