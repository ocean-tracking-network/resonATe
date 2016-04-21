import jinja2 as jin
import os

ENV = jin.Environment(loader=jin.PackageLoader('common_python', 'templates'))
SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )

d = open(SCRIPT_PATH+'/datadirectory.txt', 'r')
d = d.readline().splitlines()
DATADIRECTORY = d[0]

def create_leafelet_timeline(title, json, zoom=8):
    template = ENV.get_template('leaflet_timeline.html')

    html = template.render(title = title, json_file=DATADIRECTORY+json, zoom=zoom)
    output = open(DATADIRECTORY+title+".html", 'w')
    output.write(html)
    output.close()

    return html
