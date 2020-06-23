# import datetime
# from datetime import time as t
# from datetime import datetime as dt
# from datetime import date as real_date
# import json
#
# from django.contrib.auth.models import User
# from django_plotly_dash import DjangoDash
#
# import dash
# import dash_html_components as html
# import dash_core_components as dcc
# from dash.dependencies import Input, Output
#
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
#
# from . import DataFrameDate
# from QuitSoonApp.modules import (
#     SmokeStats, HealthyStats
#     )
# from QuitSoonApp.models import UserProfile
# from QuitSoonApp.modules.pd_user_data import hour
#
#
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#
# app = DjangoDash('TimeCigGraph', external_stylesheets=external_stylesheets)
#
# def fig(serie):
#     fig = go.Figure()
#     fig.update_layout(
#         title_text="Consommation moyenne par heure",
#         paper_bgcolor='#27293d',
#         plot_bgcolor='rgba(0,0,0,0)',
#         font=dict(color='white'),
#         )
#     fig.add_trace(go.Scatter(x=serie.index,
#                              y=serie.values,
#                              name="Moyenne par heure",
#                              mode='lines'))
#
#     # Set x-axis title
#     fig.update_xaxes(title_text="Heures",
#                      showgrid=False,
#                      zeroline=False,
#                      showline=False,)
#
#     # Set y-axes titles
#     fig.update_yaxes(title_text="Cigarettes",
#                      showgrid=False,
#                      zeroline=False,
#                      showline=False,)
#     return fig
#
#
# app.layout = html.Div(children=[
#     dcc.Graph(
#         id='time_graph',
#         animate=False,
#         style={"backgroundColor": "#1a2d46", 'color': '#ffffff'},
#         figure=fig(hour)
#     )
# ])
