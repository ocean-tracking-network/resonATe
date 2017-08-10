import jinja2 as jin
import common_python.geojson as gj
from IPython.display import IFrame
import os

ENV = jin.Environment(loader=jin.PackageLoader('common_python', 'templates'))
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]


'''
create_leaflet_timeline()
--------------------------
Uses Jinja to write an html file that can then be viewed through a browser
or used with other functions.


@var title - Pandas DataFrame pulled from the compressed detections CSV
@var json - JSON file name to use in for the map
@var center_y - Latitude center for map
@var center_x - Longitude center for map
@var steps - The number of increments the slider will snap to
'''


def create_leaflet_timeline(title, json, center_y=0, center_x=0, zoom=8, steps=100000, basemap='dark_layer'):


    template = ENV.get_template('leaflet_timeline.html')

    html = template.render(title=title, json_file=json, zoom=zoom, center_y=center_y, center_x=center_x, steps=steps, layer=basemap)
    output = open(DATADIRECTORY+"html/"+title+".html", 'w')

    print "Writing html file to "+DATADIRECTORY+"html/"+title+".html..."

    output.write(html)
    output.close()

    return "HTML file written to "+DATADIRECTORY+"html/"+title+".html"


'''
render_map()
------------
Returns and IFrame with Leaflet Timeline map of a limited number
of compressed detections

@var det_file - The CSV file of compressed or non-compressed detections to be used
@var title - The title of the html file
@var dets_table - The table to be used to get the location of the stations
@var width - The width of the iframe
@var height - The height of the iframe
@var zoom - The initial zoom of the map
'''


def render_map(det_file, title, dets_table='', width=900, height=450, zoom=8, basemap='dark_layer'):
    # Create html subfolder for output if there's not one already.
    if not os.path.exists('%s/html' % DATADIRECTORY):
        os.makedirs('%s/html' % DATADIRECTORY)

    # Create the GeoJSON to be used
    json = gj.create_geojson(det_file, dets_table=dets_table)

    if not json:
        print 'Unable to create map, please resolve issues listed above.'
        return None

    # Create the HTML and javascript that will be used for the map
    create_leaflet_timeline(json=json['filename'], title=title, center_y=json['center_y'], center_x=json['center_x'], zoom=zoom, basemap=basemap)

    # Create and return the IFrame to be rendered for the user
    iframe = IFrame('../data/html/'+title+'.html', width=width, height=height)

    return iframe
