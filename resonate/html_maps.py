import jinja2 as jin
import pandas as pd
import resonate.geojson as gj
from IPython.display import IFrame
import os

template_file = os.path.join(os.path.dirname(__file__),
                             'templates/leaflet_timeline.html')


def create_leaflet_timeline(title, json, center_y=0, center_x=0, zoom=8,
                            steps=100000, basemap='dark_layer'):
    '''
    Uses Jinja to write an html file that can then be viewed through a browser
    or used with other functions.


    :param title: Pandas DataFrame pulled from the compressed detections CSV
    :param json: JSON file name to use in for the map
    :param center_y: Latitude center for map
    :param center_x: Longitude center for map
    :param steps: The number of increments the slider will snap to
    '''

    template = jin.Template(open(template_file, 'r').read())
    html = template.render(title=title, json_file=json, zoom=zoom, center_y=center_y, center_x=center_x, steps=steps, layer=basemap)
    output = open("./html/"+title+".html", 'w')

    print("Writing html file to ./html/"+title+".html...")

    output.write(html)
    output.close()

    return "HTML file written to ./html/"+title+".html"


def render_map(dets, title, width=900, height=450,
               zoom=8, basemap='dark_layer'):
    """
    Return an IFrame with Leaflet Timeline map of a limited number of
    compressed detections.

    :param det_file: The CSV file of compressed or non-compressed detections to
        be used
    :param title: The title of the html file
    :param width: The width of the iframe
    :param height: The height of the iframe
    :param zoom: The initial zoom of the map

    :return: An iFrame containing the detections map
    """
    # Create html subfolder for output if there's not one already.
    if not os.path.exists('./html'):
        os.makedirs('./html')

    # Create the GeoJSON to be used
    json = gj.create_geojson(dets, title=title)

    if not json:
        print('Unable to create map, please resolve issues listed above.')
        return None

    # Create the HTML and javascript that will be used for the map
    create_leaflet_timeline(json=json['filename'],
                            title=title,
                            center_y=json['center_y'],
                            center_x=json['center_x'],
                            zoom=zoom,
                            basemap=basemap)

    # Create and return the IFrame to be rendered for the user
    iframe = IFrame('./html/'+title+'.html', width=width, height=height)

    return iframe
