-- Function: f_det_compressed()

-- DROP FUNCTION f_det_compressed();

CREATE OR REPLACE FUNCTION f_det_compressed()
  RETURNS text AS
$BODY$
DECLARE
    rows 		record;
    rows_snd 	record;
    total_det   	integer;
    record_cnt  	integer;

    prev_catnum  	varchar;
    prev_station		varchar;
    cur_catnum  	varchar;
    cur_station 		text;
    cur_count		integer;
    cur_startdate	timestamp without time zone;
    cur_enddate	timestamp without time zone;
    cur_startid 		text;
    cur_endid 		text;
    cur_tmp_count 	integer;
    cur_seq	integer;
 
BEGIN

	prev_catnum 	:= 'first';
	total_det       := 0;
	record_cnt      := 0;


for rows in (
	    select  *
	    from mv_anm_detections
	    order by catalognumber,datecollected
	) --end for

	LOOP

           if prev_catnum = 'first' or (prev_catnum = rows.catalognumber and prev_station = rows.station) then  
		-- skip this
	   else
		-- insert a record for the previous sequence
		total_det	:= total_det + cur_count;
		record_cnt	:= record_cnt + 1;

		--select * from mv_anm_compressed
		insert into mv_anm_compressed (catalognumber,station,seq_num,startdate,enddate,startunqdetecid,endunqdetecid,total_count)
		VALUES (cur_catnum,cur_station,cur_seq,cur_startdate,cur_enddate,cur_startid,cur_endid,cur_count);
	   end if;
	   
	--select * from mv_anm_detections limit 10
	--initalize values for first catalognumber or new catalognumber
	   if prev_catnum != rows.catalognumber then    -- reset all the columns for the catalognumber
	      prev_catnum	:= rows.catalognumber;
	      prev_station 	:= rows.station;
	      cur_catnum   	:= rows.catalognumber;
	      cur_station  	:= rows.station;
	      cur_startdate  	:= rows.datecollected;
	      cur_enddate  	:= rows.datecollected;
	      cur_startid     	:= rows.unqdetecid;
	      cur_endid      	:= rows.unqdetecid;
	      
	      cur_seq		:= 1;
      	      cur_count	   	:= 0;
      	      cur_tmp_count 	:= 0;
      	   end if;
      	      
      	   if prev_station != rows.station  then    -- reset all the columns for the station
      	      prev_station 	:= rows.station;
	      prev_station 	:= rows.station;
	      cur_catnum   	:= rows.catalognumber;
	      cur_station  	:= rows.station;
	      cur_startdate  	:= rows.datecollected;
	      cur_enddate  	:= rows.datecollected;
	      cur_startid     	:= rows.unqdetecid;
	      cur_endid      	:= rows.unqdetecid;

	      cur_seq		:= cur_seq + 1;       -- next station for this catalognumber
	      cur_count	   	:= 0;
	      cur_tmp_count 	:= 0;
           end if;
           
    	   cur_enddate  	:= rows.datecollected;  -- change the end date for each new detection at this station
    	   cur_endid      	:= rows.unqdetecid;     -- change the last id  for each new detection at this station

           cur_count	   	:= cur_count + 1;

	END LOOP; --for each record
	
	--there are no new records but last output record has not yet been inserted
	--insert the last record for the last sequence
		record_cnt	:= record_cnt + 1;
		total_det	:= total_det + cur_count;

		insert into mv_anm_compressed (catalognumber,station,seq_num,startdate,enddate,startunqdetecid,endunqdetecid,total_count)
		VALUES (cur_catnum,cur_station,cur_seq,cur_startdate,cur_enddate,cur_startid,cur_endid,cur_count);

        RETURN 'detections in file: '||total_det::text||' compressed to: '||record_cnt;

END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
GRANT EXECUTE ON FUNCTION f_det_compressed() TO public;
