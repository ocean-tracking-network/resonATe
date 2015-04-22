from . import pg_connection as pg


def view_intvl():
    """
    Creates the interval view
    """
    
    # Create Database Connection
    conn, cur = pg.createConnection() 

    # Find and drop existing view in case older versions of the view exist.
    # postgres view replace does not handle changing column sets

    drop_q = ' drop view if exists vw_interval_data'
    cur.execute(drop_q)

    query = '''
create or replace view vw_interval_data AS
SELECT
  distinct*
, case when interval_seconds=0 then null else round ( coalesce ( real_distance,distance_m )/interval_seconds,2 ) end as metres_per_second
FROM 
(
    SELECT
      fst.catalognumber
    , fst.from_station
    , fst.seq_num
    , fst.from_detcnt
    , fst.from_arrive
    , fst.from_leave
    , fst.unqdetid_from
    , snd.to_station
    , snd.to_arrive
    , snd.unqdetid_arrive
    , to_arrive-from_leave as intervaltime
    , date_part ( 'epoch',to_arrive-from_leave )::numeric as interval_seconds
    , dmtx.distance_m::numeric
    , dmtx.real_distance::numeric
    FROM
    (
        SELECT
          catalognumber
        , station as from_station
        , seq_num
        , total_count as from_detcnt
        , startdate as from_arrive
        , enddate as from_leave
        , endunqdetecid as unqdetid_from
        FROM mv_anm_compressed
    )
    fst
    LEFT JOIN
    (
        SELECT
          catalognumber
        , station as to_station
        , seq_num
        , total_count as to_detcnt
        , startdate as to_arrive
        , enddate as to_leave
        , startunqdetecid as unqdetid_arrive
        FROM mv_anm_compressed
    )
    snd
     ON fst.catalognumber=snd.catalognumber
    AND fst.seq_num=snd.seq_num-1
    LEFT JOIN
 (
    SELECT
      stn1
    , stn2
    , greatest ( 0,distance_m::numeric-coalesce ( detec_radius1::numeric,0 )- 
                    coalesce ( detec_radius2::numeric,0 ) ) as distance_m
    , case when real_distance is null then 
        null::numeric else 
        greatest ( 0,real_distance::numeric-coalesce ( detec_radius1::numeric,0 ) - 
                    coalesce ( detec_radius2::numeric,0 ) ) end 
        as real_distance
    FROM distance_matrix ) dmtx
     ON ( ( dmtx.stn1=from_station and dmtx.stn2=to_station )
    OR ( dmtx.stn2=from_station and dmtx.stn1=to_station ) )
)
foo
ORDER BY catalognumber , seq_num
'''
    
    cur.execute(query)
    conn.commit()