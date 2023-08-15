from datetime import datetime

import numpy as np
import pandas as pd
import plotly.offline as py
from plotly.graph_objs import *

py.init_notebook_mode()


def consolidate_data(detections: pd.DataFrame):
    """Takes set of detections, cleans and sumarises the detections for the
    timeline.

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of animal detections

    Returns:
        pd.DataFrame: A Pandas DataFrame of catalognumber, station, date, latitude,
        longitude and detection counts by day
    """

    detections = detections.copy(deep=True)
    if 'receiver' in detections.columns:
        detections = detections[~(detections.receiver == 'release')]
    detections['date'] = pd.to_datetime(detections.datecollected).dt.date
    detections['det_counts'] = 0
    detections = detections.groupby(
        ['catalognumber', 'date', 'station'], as_index=False, dropna=False).agg({
            'det_counts': 'count',
            'latitude': 'mean',
            'longitude': 'mean',
        })[['catalognumber',
            'date',
            'station',
            'det_counts',
            'latitude',
            'longitude']]
    detections.det_counts = (detections.det_counts / 10.0) + 5
    detections['date'] = pd.to_datetime(detections['date'])

    detections.sort_values('date', inplace=True)

    catalognumbers = pd.DataFrame(
        detections.catalognumber.unique(), columns=['catalognumber'])
    catalognumbers['color'] = catalognumbers.index + 1

    detections = detections.merge(catalognumbers, on='catalognumber')
    return detections


def create_grid(detections: pd.DataFrame):
    """Takes the a set of consolidated detections (the output from
    ``consolidate_data()``) and organizes them into a Plotly grid like format.


    Args:
        detections (pd.DataFrame): A Pandas DataFrame of catalognumber, station, date,
        latitude, longitude and detection counts by day

    Returns:
        pd.DataFrame: A Plotly grid like dataframe
    """

    total_grid = pd.DataFrame()
    for date, data in detections.groupby('date'):
        grid = pd.DataFrame()
        grid['x-' + str(date.date())] = data.longitude
        grid['y-' + str(date.date())] = data.latitude
        grid['size-' + str(date.date())] = data.det_counts
        grid['station-' + str(date.date())] = data.station
        grid['color-' + str(date.date())] = data.color
        grid['catalognumber-' + str(date.date())] = data.catalognumber
        grid.reset_index(inplace=True, drop=True)
        total_grid = pd.concat([total_grid, grid], ignore_index=False, axis=1)
    return total_grid


def create_trace(detections: pd.DataFrame, total_grid, is_mapbox=False,
                 colorscale='Viridis'):
    """

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of catalognumber, station, date,
        latitude, longitude and detection counts by day
        total_grid (pd.DataFrame): A Pandas DataFrame from ``create_grid()``
        is_mapbox (bool, optional): A boolean indicating whether to return a Scattermapbox or
        Scattergeo trace. Defaults to False.
        colorscale (str, optional):  colorscale (str, optional): A string to indicate the color index. See here for options:
        https://community.plot.ly/t/what-colorscales-are-available-in-plotly-and-which-are-the-default/2079. Defaults to 'Viridis'.

    Returns:
        Figure: A plotly scattergeo or a scattermapbox
    """
    
    trace = dict(
        lon=total_grid['x-' + str(detections.date.min().date())].dropna(),
        lat=total_grid['y-' + str(detections.date.min().date())].dropna(),
        text=total_grid['catalognumber-' +
                        str(detections.date.min().date())].dropna(),
        mode="markers",
        hoverinfo="lon+lat+text",
        marker=dict(
            size=total_grid['size-' +
                            str(detections.date.min().date())].dropna(),
            color=total_grid['color-' +
                             str(detections.date.min().date())].dropna(),
            cmin=detections.color.min(),
            cmax=detections.color.max(),
            autocolorscale=False,
            colorscale=colorscale
        )

    )
    if is_mapbox:
        trace = Scattermapbox(trace)
    else:
        trace = Scattergeo(trace)
    return trace


def create_frames(detections: pd.DataFrame, total_grid: pd.DataFrame, is_mapbox=False):
    """

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of catalognumber, station, date,
        latitude, longitude and detection counts by day
        total_grid (pd.DataFrame): A Pandas DataFrame from ``create_grid()``
        is_mapbox (bool, optional): A boolean indicating whether to return a Scattermapbox or
        Scattergeo trace. Defaults to False.

    Returns:
        list: An array of Plotly Frames
    """
    frames = []
    for date in pd.date_range(detections.date.min(), detections.date.max()):
        date = date.date()

        if 'x-' + str(date) in total_grid.columns:
            frame_trace = dict(
                lon=total_grid['x-' + str(date)].dropna(),
                lat=total_grid['y-' + str(date)].dropna(),
                text=total_grid['catalognumber-' + str(date)].dropna(),
                mode="markers",
                hoverinfo="lon+lat+text",
                marker=dict(
                    size=total_grid['size-' + str(date)].dropna(),
                    color=total_grid['color-' + str(date)].dropna()
                )
            )
        else:
            frame_trace = dict(
                lon=[0],
                lat=[0],
                text=[0],
                mode="markers",
                marker=dict(
                    size=[0]
                )
            )

        if is_mapbox:
            date_trace = Scattermapbox(frame_trace)
        else:
            date_trace = Scattergeo(frame_trace)
        frame = Frame(
            name=str(date),
            data=[date_trace],
            traces=[0]
        )

        frames = pd.concat([frames, frame])
    return frames


def define_updatemenus(animation_time=1000, transition_time=300):
    """

    Args:
        animation_time (int, optional): The amount of time in milliseconds for each frame. Defaults to 1000.
        transition_time (int, optional): The amount of time in milliseconds between frames. Defaults to 300.

    Returns:
        dict: dictionary of updatemenu settings
    """
    updatemenus = dict(
        # GENERAL
        type="buttons",
        showactive=False,
        x=0.1,
        y=0,
        pad=dict(t=60, r=10),
        xanchor="right",
        yanchor="top",
        direction="left",

        # Buttons
        buttons=[
            dict(
                method="animate",
                label="Play",

                args=[
                    None,
                    dict(
                        # False quicker but disables animations
                        frame=dict(duration=animation_time, redraw=False),
                        fromcurrent=True,
                        # easing = "cubic-in-out"
                        transition=dict(duration=transition_time,
                                        easing="quadratic-in-out"),
                        mode="immediate",
                    ),
                ],
            ),
            dict(
                method="animate",
                label="Pause",

                # PAUSE
                args=[
                    [None],  # Note the list
                    dict(
                        frame=dict(duration=0, redraw=False),  # Idem
                        mode="immediate",
                        transition=dict(duration=0),
                    ),
                ],
            ),
        ],
    )
    return updatemenus


def define_sliders(detections: pd.DataFrame, animation_time=300, slider_transition_time=300):
    """

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of catalognumber, station, date,
        latitude, longitude and detection counts by day
        animation_time (int, optional): The amount of time in milliseconds between frames. Defaults to 300.
        slider_transition_time (int, optional): The amount of time in milliseconds between
        frames for the slider. Defaults to 300.

    Returns:
        dict: A Plotly sliders dictionary
    """
    sliders = dict(
        active=0,
        steps=[],

        currentvalue=dict(
            font=dict(size=16),
            prefix="Year : ",
            xanchor="right",
            visible=True,
        ),
        transition=dict(
            duration=slider_transition_time,
            easing="cubic-in-out",
        ),

        # PLACEMENT
        x=0.1,
        y=0,
        pad=dict(t=40, b=10),
        len=0.9,
        xanchor="left",
        yanchor="top",
    )

    for date in pd.date_range(detections.date.min(), detections.date.max()):
        date = date.date()
        slider_step = dict(

            # GENERAL
            method="animate",
            value=str(date),
            label=str(date),

            # ARGUMENTS
            args=[
                [str(date)],
                dict(
                    frame=dict(duration=animation_time, redraw=False),
                    transition=dict(duration=slider_transition_time),
                    mode="immediate",
                ),
            ],

        )

        sliders["steps"].append(slider_step)
    return sliders


def define_layout(detections: pd.DataFrame, title, plotly_geo=None,  mapbox_token=None,
                  style='light'):
    """

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of catalognumber, station, date,
        latitude, longitude and detection counts by day
        title (str): the title of the plot
        plotly_geo (dict, optional): an optional dictionary to control the
        geographic aspects of the plot. Defaults to None.
        mapbox_token (str, optional): A string of mapbox access token. Defaults to None.
        style (str, optional): The style for the Mapbox tileset:
        https://plot.ly/python/reference/#layout-mapbox-style. 
        Defaults to 'light'.

    Returns:
        dict: A plotly layout dictionary
    """

    if mapbox_token is None:
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
        layout = dict(
            geo=plotly_geo,
            title=title,
            hovermode='closest',
            showlegend=False,
        )
    else:
        mapbox = dict(
            accesstoken=mapbox_token,
            center=dict(
                lon=detections.longitude.mean(),
                lat=detections.latitude.mean()
            ),
            zoom=5,
            style=style
        )
        layout = dict(title=title,
                      autosize=True,
                      hovermode='closest',
                      showlegend=False,
                      mapbox=mapbox
                      )
    return layout


def timeline(detections: pd.DataFrame, title='Timeline', height=700, width=1000,
             ipython_display=True, mapbox_token=None, plotly_geo=None,
             animation_time=1000, transition_time=300,
             slider_transition_time=300, colorscale='Rainbow', style='light'):
    
    """

    Args:
        detections (pd.DataFrame): A Pandas DataFrame of catalognumber, station, date,
        latitude, longitude and detection counts by day
        title (str, optional): the title of the plot. Defaults to 'Timeline'.
        height (int, optional): the height of the plotly. Defaults to 700.
        width (int, optional): the width of the plotly. Defaults to 1000.
        ipython_display (bool, optional): a boolean to show in a notebook. Defaults to True.
        mapbox_token (str, optional): A string of mapbox access token. Defaults to None.
        plotly_geo (dict, optional): an optional dictionary to control the
        geographic aspects of the plot. Defaults to None.
        animation_time (int, optional): The amount of time in milliseconds for each frame. Defaults to 1000.
        transition_time (int, optional): The amount of time in milliseconds between frames. Defaults to 300.
        slider_transition_time (int, optional): The amount of time in milliseconds between
        frames for the slider. Defaults to 300.
        colorscale (str, optional): A string to indicate the color index. See here for options:
        https://community.plot.ly/t/what-colorscales-are-available-in-plotly-and-which-are-the-default/2079. Defaults to 'Rainbow'.
        style (str, optional): The style for the Mapbox tileset:
        https://plot.ly/python/reference/#layout-mapbox-style 
        Defaults to 'light'.

    Returns:
        (None|Any): : A plotly object or None if ipython_display is True
    """
    detections = consolidate_data(detections)
    total_grid = create_grid(detections)
    if mapbox_token is None:
        trace = create_trace(detections, total_grid, colorscale=colorscale)
        frames = create_frames(detections, total_grid)
    else:
        trace = create_trace(detections, total_grid,
                             is_mapbox=True, colorscale=colorscale)
        frames = create_frames(detections, total_grid, is_mapbox=True)
    updatemenus = define_updatemenus(animation_time, transition_time)
    sliders = define_sliders(detections, animation_time,
                             slider_transition_time)
    layout = define_layout(detections, title, plotly_geo=plotly_geo, mapbox_token=mapbox_token,
                           style=style)

    layout.update(dict(
        updatemenus=[updatemenus],
        sliders=[sliders],
    ))

    layout.update(
        height=height,
        width=width
    )

    if ipython_display:
        fig = {'data': [trace], 'layout': layout, 'frames': frames}

        py.init_notebook_mode()
        return py.iplot(fig)
    else:
        fig = {'data': [trace], 'layout': layout, 'frames': frames}
        return py.plot(fig, filename="{}.html".format(
            title.lower().replace(" ", "_")))
