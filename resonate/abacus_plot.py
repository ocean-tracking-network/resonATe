import pandas as pd
import plotly.graph_objs as go
import plotly.offline as py
from resonate.library.exceptions import GenericException


def abacus_plot(detections, ycolumn='catalognumber', color_column=None, ipython_display=True, title='Abacus Plot', filename=None):
    '''
    Creates a plotly abacus plot from a pandas dataframe

    :param detections: detection dataframe
    :param ycolumn: the series/column for the y axis of the plot
    :param color_column: the series/column to group by and assign a color
    :param ipython_display: a boolean to show in a notebook
    :param title: the title of the plot
    :param filename: Plotly filename to write to

    :return: A plotly scatter plot
    '''

    if not isinstance(detections, pd.DataFrame):
        raise GenericException('input parameter must be a Pandas dataframe')

    mandatory_columns = set(['datecollected', ycolumn])

    if color_column is not None:
        mandatory_columns.add(color_column)

    if mandatory_columns.issubset(detections.columns):

        detections = detections[~detections.unqdetecid.str.contains(
            'release')].reset_index(drop=True)

        if color_column is not None:
            data = list()

            for group in detections.groupby(color_column):
                data.append(
                    {
                        'x': group[1].datecollected.tolist(),
                        'y': group[1][ycolumn].tolist(),
                        'mode': 'markers',
                        'name': group[0]
                    }
                )
        else:
            data = [
                {
                    'x': detections.datecollected.tolist(),
                    'y': detections[ycolumn].tolist(),
                    'mode': 'markers',
                }
            ]

        layout = dict(
            title=title,
            xaxis=dict(
                autorange=False,
                range=[detections.datecollected.min(
                ), detections.datecollected.max()]
            ),
            yaxis=dict(
                autorange=True
            ),
            margin=dict(
                l=175
            )
        )

        fig = {'data': data, 'layout': layout}

        if ipython_display:
            py.init_notebook_mode()
            return py.iplot(fig)
        else:
            return py.plot(fig, filename=filename)
    else:
        raise GenericException("Missing required input columns: {}".format(
            mandatory_columns - set(detections.columns)))
