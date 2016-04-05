import pandas as pd
import datetime
import simplejson as json
import common_python.compress as cp
from library import pg_connection as pg
import Jinja2 as jinja


d = open('common_python/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]


def unix_time_millis(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    date = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    return (date - epoch).total_seconds() * 1000.0

'''
get_station_location()
----------------------

Returns the longitude and latitude of a station/receiver given the station
and the table name.

@var station - String that contains the station name
@var table - the table name in which to find the station
'''


def get_station_locations(station, table):
    db = pg.get_engine()
    location = pd.read_sql("SELECT DISTINCT station, latitude, longitude FROM %s WHERE station IN ('%s')" % (table, '\',\''.join(station)), db)

    return location


def create_geojson(detections, dets_table=''):
    # Create a DataFrame from the CSV
    full_path_detections = "%s%s" % (DATADIRECTORY, detections)
    dets = pd.read_csv(full_path_detections)

    if not (set(['startdate', 'enddate', 'station']).issubset(dets.columns)):
        full_path_detections = cp.CompressDetections(detections)
        dets = pd.read_csv(full_path_detections)

    # Remove any release locations
    dets = dets[~dets['startunqdetecid'].astype(str).str.contains("release")]

    if dets_table == '':
        dets_table = full_path_detections.lower().replace('_compressed_detections', '').replace(DATADIRECTORY, '').replace('.csv', '')

    locs = get_station_locations(dets.station.unique().astype(str), dets_table)

    data = pd.merge(locs, dets, on='station', how='inner')
    data['startdate'] = data['startdate'].map(unix_time_millis)
    data['enddate'] = data['enddate'].map(unix_time_millis)
    data = data.sort_values(by='startdate', ascending=True)
    data.reset_index(drop=True, inplace=True)
    data.index += 1

    hue_increment = 360/data.catalognumber.unique().size
    animals = pd.DataFrame(data.catalognumber.unique())
    animals['hue'] = animals.index*hue_increment
    animals.columns = ['animals','hue']
    animals = animals.set_index(['animals'])
    animals = animals.T.to_dict()

    inc = 5000
    detection_geojson = []
    start = 1
    end = inc


    while start < data.index.size:
        geojson ={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [d["longitude"], d["latitude"]],
                    },
                    "starttime": d['startdate'],
                    "endtime": d['enddate'],
                    "catalognumber": d['catalognumber'],
                    "station": d['station'],
                    'hue': str(animals[d['catalognumber']]['hue'])
                } for index, d in data[start:end].iterrows()]
        }

        detection_geojson.append(geojson)
        start = end
        end += inc


    json_name = full_path_detections.lower().replace('.csv', '')
    output = open(json_name+".json", 'w')
    json.dump(detection_geojson, output)
    output.close()

    return detection_geojson

def create_html():
    
    return html
