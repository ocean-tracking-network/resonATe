from . import pg_connection as pg

def view_intvl():
    '''
    Creates the interval view
    '''
    
    # Create Database Connection
    conn, cur = pg.createConnection() 
    
    query = '''
create or replace view vw_interval_data AS
select distinct * ,case when interval_seconds = 0 then null
         else round( coalesce (real_distance,distance_m)/interval_seconds,2) 
         end as metres_per_second from (
select fst.*, snd.to_station, snd.to_arrive, to_arrive -from_leave as intervaltime  
,date_part('epoch',to_arrive - from_leave)::numeric as interval_seconds
,dmtx.distance_m::numeric,dmtx.real_distance::numeric from (
select catalognumber,station as from_station,seq_num,total_count as from_detcnt,startdate as from_arrive, enddate as from_leave from mv_anm_compressed )fst
left join 
(select catalognumber,station as to_station,seq_num,total_count as to_detcnt,startdate as to_arrive, enddate as to_leave from mv_anm_compressed )snd
on fst.catalognumber = snd.catalognumber
and fst.seq_num = snd.seq_num -1
left join distance_matrix dmtx
on ((dmtx.stn1 = from_station and dmtx.stn2 = to_station)
or (dmtx.stn2 = from_station and dmtx.stn1 = to_station))
) foo order by catalognumber, seq_num
'''
    
    cur.execute(query)
    conn.commit()