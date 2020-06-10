from datetime import time as t
from datetime import datetime as dt
from datetime import date as dtdate
import json

from django.contrib.auth.models import User
from django_plotly_dash import DjangoDash

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import plotly.graph_objects as go

from . import SmokeStats, DataFrameDate


with open('user_dict.txt') as json_file:
    user_dict = json.load(json_file)
    i=0
    for p in user_dict['date']:
        user_dict['date'][i] = dt.strptime(p, '%Y-%m-%d')
        i += 1

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('ConsoCigGraph', external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.RadioItems(id='my-radio',
                 options=[
                    {'label': 'Jour', 'value':'D'},
                    {'label': 'Semaine', 'value':'W'},
                    {'label': 'Mois', 'value':'M'},
                    {'label': 'Année', 'value':'Y'},
                 ],
                 value='D',
                 labelStyle={'display': 'inline-block'}
                 ),
    dcc.Graph(id='graph', animate=False, style={"backgroundColor": "#1a2d46", 'color': '#ffffff'}),
    html.Div(id='updatemode-output-container', style={'margin-top':20})
])

@app.callback(
    [Output('graph', 'figure'), Output('updatemode-output-container', 'children')],
    [Input('my-radio', 'value')]
)
def display_value(value):
    df = DataFrameDate(user_dict)
    if value == 'D':
        df = df.day_df
    elif value == 'W':
        df = df.week_df
    elif value == 'M':
        df = df.month_df
    elif value == 'Y':
        df = df.year_df

    graph = go.Bar(
        x=df.index,
        y=df.nb_cig,
        name='Manipulate Graph',
    )
    layout = go.Layout(
        paper_bgcolor='#27293d',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[min(df.index), max(df.index)]),
        yaxis=dict(range=[min(df.nb_cig), max(df.nb_cig)]),
        font=dict(color='white'),

    )
    return {'data': [graph], 'layout': layout}, {'data': [graph], 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
