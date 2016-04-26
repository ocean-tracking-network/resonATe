import pandas as pd
import os, sys
import datetime
import simplejson as json
import common_python.compress as cp
from library import pg_connection as pg


SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]


'''
unix_time_millis(dt)
-------------------
Returns a datetime in milliseconds

@var dt - datetime/timestamp
'''


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

    if db.has_table(table):
        location = pd.read_sql("SELECT DISTINCT station, latitude, longitude FROM %s WHERE station IN ('%s')" % (table, '\',\''.join(station)), db)
    else:
        print "The table '%s' does not exist. Please enter table through the dets_table argument." % table
        sys.exit(1)
    return location

'''
create_geojson()
----------------
This function maps a compressed file and converts the necessary fields
into a GeoJSON file that can be easily read by Leaflet

@var detections - a compressed or uncompressed csv detections file
@var dets_table - An override variable if the table does not match the name file name
@inc inc - the number of detections to include in each subection of the json
'''
def create_geojson(detections, dets_table='', inc=5000):
    # Create a DataFrame from the CSV
    full_path_detections = "%s%s" % (DATADIRECTORY, detections)
    dets = pd.read_csv(full_path_detections)

    # determine if the file needs to be compressed
    if not (set(['startdate', 'enddate', 'station']).issubset(dets.columns)):
        full_path_detections = cp.CompressDetections(detections)
        dets = pd.read_csv(full_path_detections)

    # Remove any release locations
    dets = dets[~dets['startunqdetecid'].astype(str).str.contains("release")]

    # Generate the table name from the file, if needed
    if dets_table == '':
        dets_table = full_path_detections.lower().replace('_compressed_detections', '').replace(DATADIRECTORY, '').replace('.csv', '')

    # Get a list of the unique stations
    locs = get_station_locations(dets.station.unique().astype(str), dets_table)
    locs = locs.drop_duplicates(subset='station')

    # Add the station location to the compressed detections
    data = pd.merge(locs, dets, on='station', how='inner')

    # Convert startdate and enddate to a milliseconds
    data['startdate'] = data['startdate'].map(unix_time_millis)
    data['enddate'] = data['enddate'].map(unix_time_millis)

    # Sort by start date and reset the index to 1
    data = data.sort_values(by='startdate', ascending=True)
    data.reset_index(drop=True, inplace=True)
    data.index += 1

    # Create a hue index for each individual catalognumber and return a dictionary
    hue_increment = 360/data.catalognumber.unique().size
    animals = pd.DataFrame(data.catalognumber.unique())
    animals['hue'] = animals.index*hue_increment
    animals.columns = ['animals','hue']
    animals = animals.set_index(['animals'])
    animals = animals.T.to_dict()

    detection_geojson = []

    # Get center points fro the map
    center_y = data.latitude.median()
    center_x = data.longitude.median()


    start = 1
    end = inc
    cap = 100000

    # Loop through the detections and create sets of geojson detections the size of the increment
    while start < data.index.size and start <= cap:
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
        # Add the set of detections to the list
        detection_geojson.append(geojson)
        start = end+1
        end += inc

    # Print message if there are more than cap for detections, defaulting to 100000
    if start > cap:
        print "Only first "+str(cap)+" detections used, please subset your data to see more."

    # Write the geojson out to a jason file
    json_name = full_path_detections.lower().replace('.csv', '').replace('data/', 'data/html/')
    print "Writing JSON file to " +json_name+".json"
    output = open(json_name+".json", 'w')
    json.dump(detection_geojson, output)
    output.close()

    # Create string with just the file name and no path
    filename = json_name.replace(DATADIRECTORY+"html/", '')+".json"

    # Return the json object, filename, and the center points
    return {'json': detection_geojson, 'filename': filename, 'center_x': center_x, 'center_y': center_y}

