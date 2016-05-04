--SQL Script used to list the tables in the public schema
SELECT
  table_schema
, table_name
FROM information_schema.tables
WHERE table_schema IN ( 'public' )

AND table_name not IN  ( 'geography_columns','geometry_columns','raster_columns','raster_overviews','spatial_ref_sys' )
AND table_type IS DISTINCT FROM  'VIEW'