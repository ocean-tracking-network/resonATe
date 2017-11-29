import pandas as pd
import os, sys
import datetime
import simplejson as json
import resonate.compress as cp


def unix_time_millis(dt):
    """
    Returns a datetime in milliseconds

    :param dt: datetime/timestamp
    :return: datetime in milliseconds
    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0



def create_geojson(detections, title, dets_table='', inc=5000):
    """
    This function maps a compressed file and converts the necessary fields
    into a GeoJSON file that can be easily read by Leaflet

    :param detections: a compressed or uncompressed csv detections file
    :param dets_table: An override variable if the table does not match the
        file name
    :param inc: the number of detections to include in each subection of
        the json

    :return: JSON object, the filename, center_x, center_y

    """
    dets = cp.compress_detections(detections)

    # Remove any release locations
    dets = dets[~dets['startunqdetecid'].astype(str).str.contains("release")]


    # Get a list of the unique stations
    locs = detections[['station', 'longitude', 'latitude']].drop_duplicates(subset='station')

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
        print("Only first "+str(cap)+" detections used, please subset your data to see more.")

    # Write the geojson out to a json file
    json_name = title.lower().replace(' ', '_')
    print("Writing JSON file to " +json_name+".json")
    output = open("./html/"+json_name+".json", 'w')
    json.dump(detection_geojson, output)
    output.close()

    # Create string with just the file name and no path
    filename = json_name.replace("./html/", '')+".json"

    # Return the json object, filename, and the center points
    return {'json': detection_geojson, 'filename': filename, 'center_x': center_x, 'center_y': center_y}
