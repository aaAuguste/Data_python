from dash import dcc, html, Input, Output, callback
from ..utils import common_functions
from ..app import app

df = common_functions.load_clean_data()

magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=df['mag'].min(),
    max=df['mag'].max(),
    step=0.1,
    value=[df['mag'].min(), df['mag'].max()],
    marks={str(int(mag)): str(int(mag)) for mag in range(int(df['mag'].min()), int(df['mag'].max())+1)}
)

map_style_dropdown = dcc.Dropdown(
    id='map-style-dropdown',
    options=[
        {'label': 'Open Street Map', 'value': 'open-street-map'},
        {'label': 'Satellite (Esri)', 'value': 'satellite-esri'},
        {'label': 'Océans (Esri Ocean Base)', 'value': 'ocean-esri'},
        {'label': 'Carto Positron', 'value': 'carto-positron'},
        {'label': 'Carto Darkmatter', 'value': 'carto-darkmatter'}
    ],
    value='open-street-map',
    clearable=False
)




earthquake_component = html.Div([
    html.Div([
        html.Label("Sélectionnez la plage de magnitude", style={"font-weight": "bold", "margin-bottom": "10px"}),
        magnitude_selection,
    ], style={"margin-bottom": "20px"}),

    html.Div([
        dcc.Graph(id='histogram', className="graph-container"),  
    ], style={"margin-bottom": "20px"}),

    html.Div([
        html.Label("Choisissez le style de la carte", style={"font-weight": "bold", "margin-top": "20px", "margin-bottom": "10px"}),
        map_style_dropdown
    ], style={"margin-bottom": "20px"}),

    html.Div([
        dcc.Graph(id='map', className="graph-container", config={'scrollZoom': True}),  
    ])
], style={"padding": "20px", "background-color": "#f8f9fa", "border-radius": "10px"})

@callback(
    Output('histogram', 'figure'),
    Output('map', 'figure'),
    Input('magnitude-slider', 'value'),
    Input('map-style-dropdown', 'value')
)
def update_visuals(magnitude_range, map_style):
    filtered_df = df[df['mag'].between(*magnitude_range)]
    hist_fig = common_functions.create_magnitude_histogram(filtered_df)
    map_fig = common_functions.create_earthquake_map(filtered_df, map_style=map_style)
    return hist_fig, map_fig


