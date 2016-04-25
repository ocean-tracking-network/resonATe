import jinja2 as jin
import common_python.geojson as gj
from IPython.display import IFrame
import os

ENV = jin.Environment(loader=jin.PackageLoader('common_python', 'templates'))
SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__))

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

'''
create_leafelet_timeline()
--------------------------



@var title - Pandas DataFrame pulled from the compressed detections CSV
@var json - JSON file name to use in for the map
@var center_y - Latitude center for map
@var center_x - Longitude center for map
'''


def create_leafelet_timeline(title, json, center_y=0, center_x=0, zoom=8, steps=100000):
    template = ENV.get_template('leaflet_timeline.html')

    html = template.render(title=title, json_file=json, zoom=zoom, center_y=center_y, center_x=center_x, steps=steps)
    output = open(DATADIRECTORY+"html/"+title+".html", 'w')

    print "Writing html file to "+DATADIRECTORY+"html/"+title+".html..."

    output.write(html)
    output.close()

    return "HTML file written to "+DATADIRECTORY+"html/"+title+".html"


def render_map(det_file, title, width=900, height=450, zoom=8):
    json = gj.create_geojson(det_file)

    create_leafelet_timeline(json=json['filename'], title=title, center_y=json['center_y'], center_x=json['center_x'], zoom=zoom)

    iframe = IFrame('../data/html/'+title+'.html', width=width, height=height)

    return iframe