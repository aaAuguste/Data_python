from dash import dcc, html, Input, Output, State, callback
from ..utils import common_functions
from ..app import app

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from geopy.distance import distance as geopy_distance

#Fonction pour créer un vrai cercle géodésique
def create_geodesic_circle(lat_c, lon_c, radius_km, n_points=72):
    """
    Construit un polygone (liste de (lat, lon)) formant un cercle géodésique
    de rayon `radius_km` autour de (lat_c, lon_c).
    """
    coords = []
    step = 360 / n_points
    for i in range(n_points):
        bearing = i * step
        pt = geopy_distance(kilometers=radius_km).destination((lat_c, lon_c), bearing)
        coords.append((pt.latitude, pt.longitude))
    # On ferme le polygone
    coords.append(coords[0])
    return coords

df = common_functions.load_clean_data()
mag_min = df['mag'].min()
mag_max = df['mag'].max()

# RangeSlider
magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=mag_min,
    max=mag_max,
    step=0.1,
    value=[mag_min, mag_max],
    marks={str(int(m)): str(int(m)) for m in range(int(mag_min), int(mag_max) + 1)},
    tooltip={"placement": "bottom", "always_visible": True}
)

# Dropdown style
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
    clearable=False,
    style={"color": "#000"}
)

# Styles : Sidebar ouverte / fermée
SIDEBAR_OPEN = {
    "position": "absolute",
    "left": "0",
    "top": "0",
    "width": "300px",
    "height": "100%",
    "background-color": "#2A2E3E",
    "padding": "20px",
    "transition": "width 0.3s",
    "overflow": "auto",
    "z-index": "9999"
}
SIDEBAR_CLOSED = {
    "position": "absolute",
    "left": "0",
    "top": "0",
    "width": "0px",
    "height": "100%",
    "background-color": "#2A2E3E",
    "padding": "0px",
    "transition": "width 0.3s",
    "overflow": "hidden",
    "z-index": "9999"
}

CONTENT_STYLE_OPEN = {
    "margin-left": "320px",
    "padding": "20px"
}
CONTENT_STYLE_CLOSED = {
    "margin-left": "20px",
    "padding": "20px"
}

menu_toggle_btn = html.Button(
    "☰ Menu",
    id="menu-toggle-btn",
    n_clicks=0,
    style={
        "background-color": "#2A2E3E",
        "color": "#ffffff",
        "border": "none",
        "padding": "10px 20px",
        "font-size": "18px",
        "cursor": "pointer",
        "border-radius": "5px"
    }
)

sidebar_content = html.Div(
    id="sidebar-content",
    children=[
        html.H2("Menu", style={"text-align": "center", "color": "#ffffff", "margin-bottom": "30px"}),

        html.Div([
            html.Label("Contrôles de l'histogramme", style={"font-weight": "bold", "color": "#ffffff"}),
            magnitude_selection
        ], style={"margin-bottom": "40px"}),

        html.Div([
            html.Label("Contrôles de la carte", style={"font-weight": "bold", "color": "#ffffff"}),
            map_style_dropdown
        ], style={"margin-bottom": "40px"}),
    ],
    style={"display": "block"}
)

sidebar = html.Div(
    id="sidebar",
    children=[sidebar_content],
    style=SIDEBAR_OPEN
)

main_content = html.Div(
    id="main-content",
    children=[
        html.Div(menu_toggle_btn, style={"margin-bottom": "20px"}),

        # Histogram
        html.Div([
            dcc.Graph(id='histogram', className="graph-container"),
        ], style={"margin-bottom": "20px"}),

        # Map
        html.Div([
            dcc.Graph(id='map', className="graph-container", config={'scrollZoom': True}),
        ], style={"margin-bottom": "20px"})
    ],
    style=CONTENT_STYLE_OPEN
)

earthquake_component = html.Div(
    children=[sidebar, main_content],
    style={
        "position": "relative",
        "height": "100vh",
        "background-color": "#1B2033"
    }
)

@callback(
    Output("sidebar", "style"),
    Output("main-content", "style"),
    Input("menu-toggle-btn", "n_clicks"),
    State("sidebar", "style"),
    State("main-content", "style"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, sidebar_style, content_style):
    if not sidebar_style:
        return SIDEBAR_OPEN, CONTENT_STYLE_OPEN
    if sidebar_style.get("width") == "300px":
        return SIDEBAR_CLOSED, CONTENT_STYLE_CLOSED
    else:
        return SIDEBAR_OPEN, CONTENT_STYLE_OPEN

@callback(
    Output('histogram', 'figure'),
    Output('map', 'figure'),
    Input('magnitude-slider', 'value'),
    Input('map-style-dropdown', 'value'),
    Input('map', 'hoverData')
)
def update_visuals(mag_range, map_style, hover_data_map):
    # Filtrage
    filtered_df = df[df['mag'].between(*mag_range)]

    # 1) Histogram
    hist_fig = common_functions.create_magnitude_histogram(filtered_df)
    hist_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        plot_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF")
    )

    # 2) Map
    map_fig = common_functions.create_earthquake_map(filtered_df, map_style=map_style)
    map_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF"),
        uirevision='map_update'
    )

    # Survol carte => on calcule un cercle géodésique
    if hover_data_map:
        lat_hover = hover_data_map['points'][0]['lat']
        lon_hover = hover_data_map['points'][0]['lon']
        hovered_point = filtered_df[
            (filtered_df['latitude'] == lat_hover) & (filtered_df['longitude'] == lon_hover)
        ]
        if not hovered_point.empty:
            mag_val = hovered_point['mag'].values[0]
            radius_km = 10 ** (0.5 * mag_val + 1)

            # On utilise create_geodesic_circle
            circle_coords = create_geodesic_circle(lat_hover, lon_hover, radius_km)

            # On trace tout en un bloc
            lat_poly = [p[0] for p in circle_coords]
            lon_poly = [p[1] for p in circle_coords]

            circle_map = go.Scattermapbox(
                lat=lat_poly,
                lon=lon_poly,
                fill='toself',
                fillcolor='rgba(0,0,255,0.2)',
                line=dict(color='blue'),
                hoverinfo='skip',
                name='Zone ressentie'
            )
            map_fig.add_trace(circle_map)

    return hist_fig, map_fig
