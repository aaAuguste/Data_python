from dash import dcc, html, Input, Output, callback
from ..utils import common_functions
from ..app import app

df = common_functions.load_clean_data()

# Magnitude selection control
magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=df['mag'].min(),
    max=df['mag'].max(),
    step=0.1,
    value=[df['mag'].min(), df['mag'].max()],
    marks={str(int(mag)): str(int(mag)) for mag in range(int(df['mag'].min()), int(df['mag'].max())+1)}
)

# Layout containing both histogram and map
earthquake_component = html.Div([
    magnitude_selection,
    dcc.Graph(id='histogram'),
    dcc.Graph(id='map')
])

@callback(
    Output('histogram', 'figure'),
    Output('map', 'figure'),
    Input('magnitude-slider', 'value')
)
def update_visuals(magnitude_range):
    filtered_df = df[df['mag'].between(*magnitude_range)]
    hist_fig = common_functions.create_magnitude_histogram(filtered_df)
    map_fig = common_functions.create_earthquake_map(filtered_df)
    return hist_fig, map_fig
