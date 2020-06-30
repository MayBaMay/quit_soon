import time
import datetime
from datetime import time as t
from datetime import datetime as dt
from datetime import date as real_date
import json

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


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def create_layout(name_graph):
    return html.Div([
        html.Div([
            dcc.RadioItems(id='my-radio',
                options=[
                        {'label': 'Jour', 'value':'D'},
                        {'label': 'Semaine', 'value':'W'},
                        {'label': 'Mois', 'value':'M'},
                     ],
                     value='D',
                     labelStyle={'display': 'inline-block'}
                     ),
            dcc.Checklist(id='my-checkbox',
                options=[{'label': 'Voir mes activités saines', 'value': 'A'},],
            # value=['MTL', 'SF'],
            )],className='graph-controls'),
        dcc.Graph(id=name_graph,
                  animate=False,
                  style={"backgroundColor": "#1a2d46", 'color': '#ffffff'},
                  ),
    ])

def fig(df, checkbox, fig_name, bar_name, y_name, y_data):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Bar(x=df.index, y=y_data, name=bar_name),
        secondary_y=False,
        )

    if checkbox :
        fig.add_trace(
            go.Scatter(x=df.index, y=df.activity_duration, name="Activités saines", mode='lines'),
            secondary_y=True,
        )

    fig.update_layout(
        title_text=fig_name,
        paper_bgcolor='#27293d',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        )
    # Set x-axis title
    fig.update_xaxes(title_text="Dates")

    # Set y-axes titles
    fig.update_yaxes(title_text=y_name,
                     range=[0, max(y_data)],
                     secondary_y=False,
                     dtick=1,
                     showgrid=False,
                     zeroline=False,
                     showline=False,)
    try:
        fig.update_yaxes(title_text="Activités (en minutes)",
                         range=[0, max(df.activity_duration)],
                         secondary_y=True,
                         dtick=15,
                         showgrid=False,
                         zeroline=False,
                         showline=False,)
    except AttributeError:
        # no activities so no activity activity_duration
        pass
    return fig

def stats(user):
    # create stats objects
    smoke = SmokeStats(user, datetime.date.today())
    healthy = HealthyStats(user, datetime.date.today())
    return smoke, healthy

def get_user_infos_from_stats(smoke_stats, healthy_stats, focus):
    # generate data for graphs
    user_dict = {'date':[],
                 'activity_duration':[],
                 'nb_cig':[],
                 'money_smoked':[],
                 'nicotine':[]}
    for date in smoke_stats.list_dates:
        user_dict['date'].append(dt.combine(date, dt.min.time()))
        user_dict['activity_duration'].append(healthy_stats.report_substitut_per_period(date))
        if focus == 'nb_cig':
            user_dict['nb_cig'].append(smoke_stats.nb_per_day(date))
        elif focus == 'money_smoked':
            user_dict['money_smoked'].append(float(smoke_stats.money_smoked_per_day(date)))
        elif focus == 'nicotine':
            user_dict['nicotine'].append(healthy_stats.nicotine_per_day(date))
    return user_dict

def dataframe(radio, user_dict, focus):
    df = DataFrameDate(user_dict, focus)
    if radio == 'D':
        df = df.day_df
    elif radio == 'W':
        df = df.week_df
    elif radio == 'M':
        df = df.month_df
    return df

app1 = DjangoDash('ConsoCigGraph', external_stylesheets=external_stylesheets)
app1.layout = create_layout('graph1')
@app1.expanded_callback(
    dash.dependencies.Output('graph1', 'figure'),
    [dash.dependencies.Input('my-radio', 'value'),
    dash.dependencies.Input('my-checkbox', 'value')],
)
def display_value(radio, checkbox, request, **kwargs):
    smoke, healthy = stats(request.user)
    user_dict = get_user_infos_from_stats(smoke, healthy, 'nb_cig')
    df = dataframe(radio, user_dict, 'nb_cig')
    figure = fig(df, checkbox, "Consommation de cigarettes", "Conso cigarette", "Cigarettes", df.nb_cig)
    return figure

app2 = DjangoDash('MoneyGraph', external_stylesheets=external_stylesheets)
app2.layout = create_layout('graph2')
@app2.expanded_callback(
    dash.dependencies.Output('graph2', 'figure'),
    [dash.dependencies.Input('my-radio', 'value'),
    dash.dependencies.Input('my-checkbox', 'value')],
)
def display_value(radio, checkbox, request, **kwargs):
    smoke, healthy = stats(request.user)
    user_dict = get_user_infos_from_stats(smoke, healthy, 'money_smoked')
    df = dataframe(radio, user_dict, 'money_smoked')
    figure = fig(df, checkbox, "Argent parti en fumée", "Argent dépensé (en €)", "Mes sous", df.money_smoked)
    return figure

app3 = DjangoDash('NicotineGraph', external_stylesheets=external_stylesheets)
app3.layout = create_layout('graph3')
@app3.expanded_callback(
    dash.dependencies.Output('graph3', 'figure'),
    [dash.dependencies.Input('my-radio', 'value'),
    dash.dependencies.Input('my-checkbox', 'value')],
)
def display_value(radio, checkbox, request, **kwargs):
    smoke, healthy = stats(request.user)
    user_dict = get_user_infos_from_stats(smoke, healthy, 'nicotine')
    df = dataframe(radio, user_dict, 'nicotine')
    figure = fig(df, checkbox, "Consomation de substitut nicotinique", "Nicotine (en mg)", "Nicotine", df.nicotine)
    return figure
