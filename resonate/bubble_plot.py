import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go
from resonate.library.exceptions import GenericException

def bubble_plot(detections, type='detections', ipython_display=True, title = 'Bubble Plot', height=700, width=1000, plotly_geo=None, filename=None):

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

    :return: A plotly geoscatter plot
    '''

    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_columns = set(['station', 'catalognumber', 'unqdetecid', 'latitude', 'longitude', 'datecollected'])


    if mandatory_columns.issubset(detections.columns):
        detections = detections[['station', 'catalognumber', 'unqdetecid', 'latitude', 'longitude', 'datecollected']]
        detections = detections[~detections.unqdetecid.str.contains('release')].reset_index(drop=True)


        if type =='individual':
            detections = detections.drop(['unqdetecid', 'datecollected'],axis=1).drop_duplicates()
        detections = detections.groupby(['station', 'latitude', 'longitude']).size().reset_index(name='counts')


        data = [
            {
                'lon': detections.longitude.tolist(),
                'lat': detections.latitude.tolist(),
                'text': detections.station+" : "+detections.counts.astype(str),
                'mode': 'markers',
                'marker': {
                    'color': detections.counts.tolist(),
                    'size':10,
                    'showscale': True,
                    'colorscale':'Viridis',
                    'colorbar':{
                        'title':'Detection Count'
                    }
                },
                'type':'scattergeo'
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


        if ipython_display:
            layout = dict(
                geo = plotly_geo,
                title = title,
                height=height,
                width=width
            )
            fig = { 'data':data, 'layout':layout }

            py.init_notebook_mode()
            return py.iplot(fig)
        else:
            layout = dict(
                geo = plotly_geo,
                title = title
            )
            fig = { 'data':data, 'layout':layout }
            return py.plot(fig, filename=filename)
    else:
        raise GenericException("Missing required input columns: {}".format(mandatory_columns - set(detections.columns)))
