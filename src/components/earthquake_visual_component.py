from dash import dcc, html, Input, Output, callback
from ..utils import common_functions
from ..app import app
import pandas as pd
import plotly.express as px

df = common_functions.load_clean_data()

magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=df['mag'].min(),
    max=df['mag'].max(),
    step=0.1,
    value=[df['mag'].min(), df['mag'].max()],
    marks={str(int(mag)): str(int(mag)) for mag in range(int(df['mag'].min()), int(df['mag'].max()) + 1)}
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
    Input('map-style-dropdown', 'value'),
    Input('map', 'hoverData')
)
def update_visuals(magnitude_range, map_style, hover_data):
    filtered_df = df[df['mag'].between(*magnitude_range)]
    hist_fig = common_functions.create_magnitude_histogram(filtered_df)
    map_fig = common_functions.create_earthquake_map(filtered_df, map_style=map_style)

    # Ajouter l'attribut uirevision pour conserver les interactions utilisateur
    map_fig.update_layout(uirevision='map_update')

    # Vérification si on survole un point
    if hover_data:
        lat_hover = hover_data['points'][0]['lat']
        lon_hover = hover_data['points'][0]['lon']

        hovered_point = filtered_df[
            (filtered_df['latitude'] == lat_hover) & (filtered_df['longitude'] == lon_hover)
        ]

        if not hovered_point.empty:
            mag_hover = hovered_point['mag'].values[0]
            radius = 10 ** (0.5 * mag_hover + 1)  

            # Ajouter le cercle autour du point survolé
            circle_df = pd.DataFrame({
                'latitude': [lat_hover],
                'longitude': [lon_hover],
                'radius': [radius]
            })
            hover_circle = px.scatter_mapbox(
                circle_df,
                lat='latitude',
                lon='longitude',
                size='radius',
                color_discrete_sequence=["blue"],
                opacity=0.3
            )

            # Ajouter les cercles comme trace supplémentaire
            map_fig.add_trace(hover_circle.data[0])

    return hist_fig, map_fig
