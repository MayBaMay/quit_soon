import datetime
from datetime import time as t
from datetime import datetime as dt
from datetime import date as real_date
import json
import pandas as pd

from django.contrib.auth.models import User
from django_plotly_dash import DjangoDash

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import DataFrameDate
from QuitSoonApp.modules import (
    SmokeStats, HealthyStats
    )
from QuitSoonApp.models import UserProfile
from QuitSoonApp.modules import SmokeStats


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('TimeCigGraph', external_stylesheets=external_stylesheets)

def generate_hour_df(user):
    """
    Function generating pandas serie with average cigarettes for hours(0 to 24)
    total cig_smoked_per_hour / average_cig/day
    """
    smoke = SmokeStats(user, datetime.date.today())
    nb_full_days = smoke.nb_full_days_since_start
    qs = smoke.user_conso_full_days.values()
    data_cig = pd.DataFrame(qs)
    data_cig['date'] = data_cig.apply(lambda r : dt.combine(r['date_cig'],r['time_cig']),1)
    data = data_cig.date.dt.hour.value_counts()
    empty_data = {}
    for hour in range(0,25):
        try:
            empty_data[hour] = data.loc[hour] / nb_full_days
        except KeyError:
            empty_data[hour] = 0
    parsed_data = pd.Series(empty_data)
    return parsed_data

def fig(serie):
    fig = go.Figure()
    fig.update_layout(
        title_text="Consommation moyenne par heure",
        paper_bgcolor='#27293d',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        )
    fig.add_trace(go.Scatter(x=serie.index,
                             y=serie.values,
                             name="Moyenne par heure",
                             mode='lines'))

    # Set x-axis title
    fig.update_xaxes(title_text="Heures",
                     dtick=1,
                     showgrid=False,
                     zeroline=False,
                     showline=False,)

    # Set y-axes titles
    fig.update_yaxes(title_text="Cigarettes",
                     dtick=1,
                     showgrid=False,
                     zeroline=False,
                     showline=False,)
    return fig


app.layout = html.Div(children=[
    dcc.Graph(
        id='time_graph',
        animate=False,
        style={"backgroundColor": "#1a2d46", 'color': '#ffffff'},
    ),
    dcc.Input(
        id='fake-input',
        placeholder='',
        type='hidden',
        value=''
    )
])

@app.expanded_callback(
    dash.dependencies.Output('time_graph', 'figure'),
    [dash.dependencies.Input('fake-input', 'value')],
)
def display_value(input, request, **kwargs):
    hour = generate_hour_df(request.user)
    return fig(hour)
