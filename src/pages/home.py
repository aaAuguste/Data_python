from dash import html
from ..components import earthquake_visual_component

layout = html.Div([
    html.H1("Earthquake Data Dashboard"),
    earthquake_visual_component.earthquake_component,

])
