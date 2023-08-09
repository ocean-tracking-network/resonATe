import pandas as pd
import plotly.graph_objs as go
import plotly.offline as py
from resonate.library.exceptions import GenericException


def bubble_plot(detections: pd.DataFrame, type='detections', ipython_display=True,
                title='Bubble Plot', height=700, width=1000,
                plotly_geo=None, filename=None, mapbox_token=None,
                marker_size=10, colorscale='Viridis'):
    """_summary_

    Args:
        detections (pd.DataFrame): detection dataframe
        type (str, optional): Counts detections if 'detection', or counts individuals if 'individual'. Defaults to 'detections'.
        ipython_display (bool, optional): a boolean to show in a notebook. Defaults to True.
        title (str, optional): the title of the plot. Defaults to 'Bubble Plot'.
        height (int, optional): the height of the plot. Defaults to 700.
        width (int, optional): the width of the plot. Defaults to 1000.
        plotly_geo (dict, optional): an optional dictionary to controle the
        geographix aspects of the plot. Defaults to None.
        filename (str, optional): Plotly filename to write to. Defaults to None.
        mapbox_token (str, optional): A string of mapbox access token. Defaults to None.
        marker_size (int, optional): An int to indicate the diameter in pixels. Defaults to 10.
        colorscale (str, optional): A string to indicate the color index. Defaults to 'Viridis'.

    Raises:
        GenericException: Triggers if detections isn't a dataframe
        GenericException: Triggers if detections is missing required columns

    Returns:
        (None|Any):  A plotly geoscatter plot or mapbox plot
    """

    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_columns = set(
        ['station', 'catalognumber', 'unqdetecid', 'latitude', 'longitude', 'datecollected'])

    if mandatory_columns.issubset(detections.columns):
        detections = detections[['station', 'catalognumber', 'unqdetecid',
                                 'latitude', 'longitude', 'datecollected']].reset_index(drop=True)

        if type == 'individual':
            detections = detections.drop(
                ['unqdetecid', 'datecollected'], axis=1).drop_duplicates()
        detections = detections.groupby(
            ['station', 'latitude', 'longitude'], dropna=False).size().reset_index(name='counts')

        map_type = 'scattergeo'

        if mapbox_token is not None:
            map_type = 'scattermapbox'
            mapbox = dict(
                accesstoken=mapbox_token,
                center=dict(
                    lon=detections.longitude.mean(),
                    lat=detections.latitude.mean()
                ),
                zoom=5,
                style='light'
            )

        data = [
            {
                'lon': detections.longitude.tolist(),
                'lat': detections.latitude.tolist(),
                'text': detections.station + " : " + detections.counts.astype(str),
                'mode': 'markers',
                'marker': {
                    'color': detections.counts.tolist(),
                    'size': marker_size,
                    'showscale': True,
                    'colorscale': colorscale,
                    'colorbar': {
                        'title': 'Detection Count'
                    }
                },
                'type': map_type
            }
        ]

        if plotly_geo is None:
            plotly_geo = dict(
                showland=True,
                landcolor="rgb(255, 255, 255)",
                showocean=True,
                oceancolor="rgb(212,212,212)",
                showlakes=True,
                lakecolor="rgb(212,212,212)",
                showrivers=True,
                rivercolor="rgb(212,212,212)",
                resolution=50,
                showcoastlines=False,
                showframe=False,
                projection=dict(
                    type='mercator',
                )
            )

        plotly_geo.update(
            center=dict(
                lon=detections.longitude.mean(),
                lat=detections.latitude.mean()
            ),
            lonaxis=dict(
                range=[detections.longitude.min(), detections.longitude.max()],
            ),
            lataxis=dict(
                range=[detections.latitude.min(), detections.latitude.max()],
            )
        )

        if mapbox_token is None:
            layout = dict(
                geo=plotly_geo,
                title=title
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
            fig = {'data': data, 'layout': layout}

            py.init_notebook_mode()
            return py.iplot(fig)
        else:
            fig = {'data': data, 'layout': layout}
            return py.plot(fig, filename=filename)
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))
