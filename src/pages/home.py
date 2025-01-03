from dash import html
from ..components import earthquake_visual_component

layout = html.Div([
    html.H1("Les Séismes en 2024"),
    html.Div([
        earthquake_visual_component.earthquake_component
    ], style={"padding": "20px", "margin": "0 auto", "max-width": "1200px"})
])
