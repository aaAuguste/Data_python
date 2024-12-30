from dash import dcc, html, Input, Output, State, callback
from ..utils import common_functions
from ..app import app

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = common_functions.load_clean_data()

mag_min = df['mag'].min()
mag_max = df['mag'].max()

total_seismes = len(df)
magnitude_moyenne = round(df['mag'].mean(), 2)
magnitude_max_ = df['mag'].max()
magnitude_min_ = df['mag'].min()

magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=mag_min,
    max=mag_max,
    step=0.1,
    value=[mag_min, mag_max],
    marks={str(int(m)): str(int(m)) for m in range(int(mag_min), int(mag_max) + 1)},
    tooltip={"placement": "bottom", "always_visible": True}
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
    clearable=False,
    style={"color": "#000"}
)

# Bouton pour toggler le menu
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

sidebar_content = html.Div(
    id="sidebar-content",
    children=[
        html.H2("Menu", style={"margin-bottom": "30px", "text-align": "center"}),

        html.Div([
            html.Label("Contrôles de l'histogramme", 
                       style={"font-weight": "bold", "color": "#ffffff", "margin-bottom": "10px"}),
            magnitude_selection
        ], style={"margin-bottom": "40px"}),

        html.Div([
            html.Label("Contrôles de la carte",
                       style={"font-weight": "bold", "color": "#ffffff", "margin-bottom": "10px"}),
            map_style_dropdown
        ], style={"margin-bottom": "40px"}),

        html.Hr(style={"border": "1px solid #ffffff"}),

        html.Div([
            html.H4("Infographies Sismiques", style={"margin-bottom": "20px"}),
            html.Div([
                html.P("Nombre total de séismes", style={"font-weight": "bold", "margin-bottom": "5px"}),
                html.P(f"{total_seismes}", style={"font-size": "24px", "margin": "0"}),
            ], className="kpi-box"),

            html.Div([
                html.P("Magnitude moyenne", style={"font-weight": "bold", "margin-bottom": "5px"}),
                html.P(f"{magnitude_moyenne}", style={"font-size": "24px", "margin": "0"}),
            ], className="kpi-box"),

            html.Div([
                html.P("Magnitude min/max", style={"font-weight": "bold", "margin-bottom": "5px"}),
                html.P(f"{magnitude_min_} / {magnitude_max_}", style={"font-size": "24px", "margin": "0"}),
            ], className="kpi-box"),
        ], style={"margin-top": "40px"})
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

        # Histogramme
        html.Div(
            dcc.Graph(id='histogram', className="graph-container"),
            style={"margin-bottom": "20px"}
        ),

        # Carte (2D)
        html.Div(
            dcc.Graph(id='map', className="graph-container", config={'scrollZoom': True})
        ),

        # Globe (3D)
        html.Div([
            html.H3("Globe 3D (projection orthographique)", style={"margin-top": "40px"}),
            dcc.Graph(id='globe', className="graph-container")
        ], style={"margin-top": "20px"})
    ],
    style=CONTENT_STYLE_OPEN
)

earthquake_component = html.Div(
    children=[sidebar, main_content],
    style={
        "position": "relative",
        "height": "100vh",
        "background-color": "transparent"
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
    Output('globe', 'figure'),
    Input('magnitude-slider', 'value'),
    Input('map-style-dropdown', 'value'),
    Input('map', 'hoverData'),
    Input('globe', 'hoverData')
)
def update_visuals(mag_range, map_style, hover_data_map, hover_data_globe):
    """
    1) Filtrage du DataFrame selon la plage de magnitude
    2) Génération histogram, carte 2D, globe 3D
    3) Ajout d'une zone ressentie *séparée* :
       - Sur la carte *seulement* si on survole la carte
       - Sur le globe *seulement* si on survole le globe
    4) Découpe manuelle du polygone si on franchit ±180°
       pour éviter le bug d'affichage (autant sur la carte que sur le globe).
    """
    filtered_df = df[df['mag'].between(*mag_range)]

    # Histogramme
    hist_fig = common_functions.create_magnitude_histogram(filtered_df)
    hist_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        plot_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF")
    )

    # Carte 2D
    map_fig = common_functions.create_earthquake_map(filtered_df, map_style=map_style)
    map_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF"),
        uirevision='map_update'
    )

    # Globe 3D 
    globe_fig = common_functions.create_globe_figure(filtered_df, globe_style=map_style)

    '''''''''''''''''''''''''''''''''''''''
    Problème sur le calcul de certaines zones particulièrement quand elle traverse le méridien 180E ou les pôles
    Donc inactif pour le moment.
    
    '''''''''''''''''''''''''''''''''''''''

    # Sur la CARTE
    # if hover_data_map:
    #     lat_hover = hover_data_map['points'][0]['lat']
    #     lon_hover = hover_data_map['points'][0]['lon']
    #     hovered_point = filtered_df[
    #         (filtered_df['latitude'] == lat_hover) & (filtered_df['longitude'] == lon_hover)
    #     ]
    #     if not hovered_point.empty:
    #         mag_val = hovered_point['mag'].values[0]
    #         radius_km = 10 ** (0.5 * mag_val + 1)
    #         circle_coords = common_functions.create_geodesic_circle(lat_hover, lon_hover, radius_km)

    #         # Découpe si ça franchit ±180°
    #         polygons_map = common_functions.split_polygon_at_dateline(circle_coords)
    #         for poly in polygons_map:
    #             lat_poly = [p[0] for p in poly]
    #             lon_poly = [p[1] for p in poly]
    #             circle_map = go.Scattermapbox(
    #                 lat=lat_poly,
    #                 lon=lon_poly,
    #                 fill='toself',
    #                 fillcolor='rgba(0, 0, 255, 0.2)',
    #                 line=dict(color='blue'),
    #                 hoverinfo='skip',
    #                 name='Zone ressentie'
    #             )
    #             map_fig.add_trace(circle_map)

    # Sur le GLOBE
    if hover_data_globe:
        lat_hover = hover_data_globe['points'][0]['lat']
        lon_hover = hover_data_globe['points'][0]['lon']
        hovered_point = filtered_df[
            (filtered_df['latitude'] == lat_hover) & (filtered_df['longitude'] == lon_hover)
        ]
        if not hovered_point.empty:
            mag_val = hovered_point['mag'].values[0]
            radius_km = 10 ** (0.5 * mag_val + 1)
            circle_coords = common_functions.create_geodesic_circle(lat_hover, lon_hover, radius_km)

            # Découpe aussi pour le globe
            polygons_globe = common_functions.split_polygon_at_dateline(circle_coords)
            for poly in polygons_globe:
                lat_poly = [p[0] for p in poly]
                lon_poly = [p[1] for p in poly]
                circle_globe = go.Scattergeo(
                    lat=lat_poly,
                    lon=lon_poly,
                    fill='toself',
                    fillcolor='rgba(0, 0, 255, 0.2)',
                    line=dict(color='blue'),
                    hoverinfo='skip',
                    name='Zone ressentie'
                )
                globe_fig.add_trace(circle_globe)

    return hist_fig, map_fig, globe_fig
