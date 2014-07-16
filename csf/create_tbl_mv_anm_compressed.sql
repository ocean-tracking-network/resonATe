-- DROP TABLE  mv_anm_compressed  

CREATE TABLE mv_anm_compressed  
(
  catalognumber text NOT NULL,
  station text NOT NULL,
  seq_num integer,
  startdate  timestamp without time zone NOT NULL,
  enddate  timestamp without time zone NOT NULL,
  startunqdetecid text NOT NULL,
  endunqdetecid text NOT NULL,
  total_count integer
);
