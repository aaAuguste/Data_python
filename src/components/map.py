from dash import dcc, html
from src.utils import common_functions

df = common_functions.load_clean_data()

map_fig = common_functions.create_earthquake_map(df)

map_component = html.Div([
    dcc.Graph(figure=map_fig)
])
