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
select distinct * ,case when interval_seconds = 0 then null
else round( coalesce (real_distance,distance_m)/interval_seconds,2)
end as metres_per_second  from (
select fst.catalognumber,fst.from_station,fst.seq_num,fst.from_detcnt
,fst.from_arrive,fst.from_leave,fst.unqdetid_from,
snd.to_station, snd.to_arrive,snd.unqdetid_arrive
, to_arrive - from_leave as intervaltime
,date_part('epoch',to_arrive - from_leave)::numeric as interval_seconds
,dmtx.distance_m::numeric,dmtx.real_distance::numeric
 from (select catalognumber,station as from_station,seq_num
,total_count as from_detcnt,startdate as from_arrive, enddate as from_leave,
endunqdetecid as unqdetid_from from mv_anm_compressed )fst
left join
(select catalognumber,station as to_station,seq_num,total_count as to_detcnt,
startdate as to_arrive, enddate as to_leave,
startunqdetecid as unqdetid_arrive from mv_anm_compressed )snd
on fst.catalognumber = snd.catalognumber
and fst.seq_num = snd.seq_num -1
left join
(select * from distance_matrix ) dmtx
on ((dmtx.stn1 = from_station and dmtx.stn2 = to_station)
or (dmtx.stn2 = from_station and dmtx.stn1 = to_station))
) foo order by catalognumber, seq_num) foo order by catalognumber, seq_num
'''
    
    cur.execute(query)
    conn.commit()