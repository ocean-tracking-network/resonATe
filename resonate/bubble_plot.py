import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go
from resonate.library.exceptions import GenericException

def bubble_plot(detections, type='detections', ipython_display=True,
                title = 'Bubble Plot', height=700, width=1000,
                plotly_geo=None, filename=None, mapbox_token=None,
                marker_size=10,colorscale='Viridis'):

    '''
    Creates a plotly abacus plot from a pandas dataframe

    :param detections: detection dataframe
    :param ipython_display: a boolean to show in a notebook
    :param title: the title of the plot
    :param height: the height of the plotl
    :param width: the width of the plotly
    :param plotly_geo: an optional dictionary to controle the
        geographix aspects of the plot
    :param filename: Plotly filename to write to
    :param mapbox_token: A string of mapbox access token
    :param marker_size: An int to indicate the diameter in pixels
    :param colorscale: A string to indicate the color index

    :return: A plotly geoscatter plot or mapbox plot
    '''

    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_columns = set(['station', 'catalognumber', 'unqdetecid', 'latitude', 'longitude', 'datecollected'])


    if mandatory_columns.issubset(detections.columns):
        detections = detections[['station', 'catalognumber', 'unqdetecid', 'latitude', 'longitude', 'datecollected']].reset_index(drop=True)


        if type =='individual':
            detections = detections.drop(['unqdetecid', 'datecollected'],axis=1).drop_duplicates()
        detections = detections.groupby(['station', 'latitude', 'longitude']).size().reset_index(name='counts')

        map_type = 'scattergeo'

        if mapbox_token is not None:
            map_type = 'scattermapbox'
            mapbox=dict(
                accesstoken=mapbox_token,
                center=dict(
                    lon = detections.longitude.mean(),
                    lat = detections.latitude.mean()
                ),
                zoom=5,
                style='light'
            )

        data = [
            {
                'lon': detections.longitude.tolist(),
                'lat': detections.latitude.tolist(),
                'text': detections.station+" : "+detections.counts.astype(str),
                'mode': 'markers',
                'marker': {
                    'color': detections.counts.tolist(),
                    'size':marker_size,
                    'showscale': True,
                    'colorscale':colorscale,
                    'colorbar':{
                        'title':'Detection Count'
                    }
                },
                'type':map_type
            }
        ]

        if plotly_geo is None:
            plotly_geo = dict(
                showland = True,
                landcolor = "rgb(255, 255, 255)",
                showocean = True,
                oceancolor = "rgb(212,212,212)",
                showlakes = True,
                lakecolor = "rgb(212,212,212)",
                showrivers = True,
                rivercolor = "rgb(212,212,212)",
                resolution = 50,
                showcoastlines = False,
                showframe=False,
                projection = dict(
                    type = 'mercator',
                )
            )

        plotly_geo.update(
            center = dict(
                lon = detections.longitude.mean(),
                lat = detections.latitude.mean()
            ),
            lonaxis = dict(
                range= [ detections.longitude.min(), detections.longitude.max()],
            ),
            lataxis = dict (
                range= [ detections.latitude.min(), detections.latitude.max()],
            )
        )


        if mapbox_token is None:
            layout = dict(
                geo = plotly_geo,
                title = title
            )
        else:
            layout = dict(title=title,
                            autosize=True,
                            hovermode='closest',
                            mapbox=mapbox
                        )

        if ipython_display:
            layout.update(
                height=height,
                width=width
            )
            fig = { 'data':data, 'layout':layout }

            py.init_notebook_mode()
            return py.iplot(fig)
        else:
            fig = { 'data':data, 'layout':layout }
            return py.plot(fig, filename=filename)
    else:
        raise GenericException("Missing required input columns: {}".format(mandatory_columns - set(detections.columns)))
