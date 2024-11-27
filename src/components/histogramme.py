from dash import dcc, html
from ... import utils

df = utils.load_clean_data()

histogram_fig = utils.create_magnitude_histogram(df)

histogram_component = html.Div([
    dcc.Graph(figure=histogram_fig)
])
