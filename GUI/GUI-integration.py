import dash
from dash import html, dcc

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Interval(id='live-update', interval=30*1000),
    html.Div(id='performance-metrics'),
    dcc.Graph(id='strategy-heatmap')
])
