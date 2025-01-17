from dash import html
from src.components import earthquake_visual_component

layout = html.Div([
    html.H1("Activités Sismiques en 2024"),
    html.Div([
        earthquake_visual_component.earthquake_component
    ], style={"padding": "20px", "margin": "0 auto", "maxWidth": "1200px"})
])
