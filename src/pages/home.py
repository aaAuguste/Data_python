from dash import html
from ..components import histogram

layout = html.Div([
    html.H1("Earthquake Data Dashboard"),
    histogram.histogram_component,
])
