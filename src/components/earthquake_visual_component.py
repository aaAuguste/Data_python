from dash import dcc, html, Input, Output, State, callback
from ..utils import common_functions
import plotly.graph_objects as go
import requests
import json

# URL du GeoJSON des frontières tectoniques
geojson_url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json"
response = requests.get(geojson_url)
tectonic_data = json.loads(response.text)

# Chargement du DataFrame des séismes
df = common_functions.load_clean_data()

# Calcul des valeurs de référence pour la plage de magnitude
mag_min = df['mag'].min()
mag_max = df['mag'].max()

# Statistiques
total_seismes = len(df)
magnitude_moyenne = round(df['mag'].mean(), 2)
magnitude_max_ = df['mag'].max()
magnitude_min_ = df['mag'].min()

# RangeSlider pour la plage de magnitude
magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=mag_min,
    max=mag_max,
    step=0.1,
    value=[mag_min, mag_max],
    marks={str(int(m)): str(int(m)) for m in range(int(mag_min), int(mag_max)+1)},
    tooltip={"placement": "bottom", "always_visible": True}
)

# Dropdown pour le style de carte (utilisé à la fois pour 2D et 3D)
map_style_dropdown = dcc.Dropdown(
    id='map-style-dropdown',
    options=[
        {'label': 'Open Street Map', 'value': 'open-street-map'},
        {'label': 'Satellite (Esri)', 'value': 'satellite-esri'},
        {'label': 'Océans (Esri)', 'value': 'ocean-esri'},
        {'label': 'Carto Positron', 'value': 'carto-positron'},
        {'label': 'Carto Darkmatter', 'value': 'carto-darkmatter'}
    ],
    value='open-street-map',
    clearable=False,
    style={"color": "#000"}
)

# RadioItems pour choisir la vue 2D ou 3D
view_switch = dcc.RadioItems(
    id="view-switch",
    options=[
        {"label": "Vue 2D", "value": "2D"},
        {"label": "Vue 3D", "value": "3D"}
    ],
    value="2D",  # par défaut
    inputStyle={"marginRight": "5px"},
    style={"color": "#fff"}
)

# Checklist pour activer/désactiver failles et séismes (uniquement en 2D)
layer_switch_2d = dcc.Checklist(
    id="layer-switch-2d",
    options=[
        {"label": "Failles tectoniques (2D)", "value": "failles"},
        {"label": "Séismes (2D)", "value": "seismes"}
    ],
    value=["failles", "seismes"],
    style={"color": "#fff"}
)

# Checklist pour afficher les zones sur le globe (3D)
zone_display_switch = dcc.Checklist(
    id="zone-display-switch",
    options=[{'label': 'Afficher zones sur le Globe (3D)', 'value': 'globe-zones'}],
    value=[],
    style={"color": "#fff"}
)

menu_toggle_btn = html.Button(
    "☰ Menu",
    id="menu-toggle-btn",
    n_clicks=0,
    className="menu-toggle-btn"
)


# Sidebar : on y place le titre, les sliders, dropdown, radio, etc.
sidebar_content = html.Div(
    children=[
        html.H2("Menu"),

        html.Label("Contrôles de la magnitude"),
        magnitude_selection,

        html.Br(),
        html.Label("Contrôles de la carte"),
        map_style_dropdown,

        html.Br(),
        html.Label("Vue 2D / 3D"),
        view_switch,

        # Ajout de la checklist pour les couches 2D
        html.Div([
            html.Br(),
            html.Label("Couches (2D)"),
            layer_switch_2d
        ], style={"marginTop": "10px"}),

        # Ajout de la checklist pour le globe 3D
        html.Div([
            html.Br(),
            html.Label("Options (3D)"),
            zone_display_switch
        ], style={"marginTop": "10px"}),

        html.Hr(),
        html.H4("Infographies Sismiques"),
        html.Div([
            html.P("Nombre total de séismes"),
            html.P(f"{total_seismes}", className="kpi-number")
        ], className="kpi-box"),
        html.Div([
            html.P("Magnitude moyenne"),
            html.P(f"{magnitude_moyenne}", className="kpi-number")
        ], className="kpi-box"),
        html.Div([
            html.P("Magnitude min/max"),
            html.P(f"{magnitude_min_} / {magnitude_max_}", className="kpi-number")
        ], className="kpi-box"),
    ],
    id="sidebar-content"
)

sidebar = html.Div(
    children=[sidebar_content],
    id="sidebar",
    className="sidebar-open"
)

# Contenu principal : histogramme + main-graph + checklists 2D & 3D
main_content = html.Div(
    id="main-content",
    className="content-open",
    children=[
        # Bouton sidebar
        html.Div(menu_toggle_btn),

        # Histogramme
        html.Div(
            dcc.Graph(id='histogram', className="graph-container"),
            style={"marginBottom" : "20px"}
        ),

        # Un seul graph pour afficher soit la vue 2D, soit la vue 3D
        html.Div(
            dcc.Graph(id='main-graph', className="graph-container", config={'scrollZoom': True})
        ),

        
    ]
)

# Assemblage final
earthquake_component = html.Div(
    children=[sidebar, main_content],
    className="earthquake-container"
)

@callback(
    Output("sidebar", "className"),
    Output("main-content", "className"),
    Input("menu-toggle-btn", "n_clicks"),
    State("sidebar", "className"),
    State("main-content", "className"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, sidebar_class, content_class):
    """
    Au clic sur le bouton menu-toggle-btn :
     - Si la sidebar est "open", on la ferme -> "sidebar-closed" + "content-closed"
     - Sinon, on l'ouvre -> "sidebar-open" + "content-open"
    """
    if not sidebar_class:
        return "sidebar-open", "content-open"

    if "sidebar-open" in sidebar_class:
        return "sidebar-closed", "content-closed"
    else:
        return "sidebar-open", "content-open"


@callback(
    Output('histogram', 'figure'),
    Output('main-graph', 'figure'),
    Input('magnitude-slider', 'value'),     # plage magnitudes
    Input('map-style-dropdown', 'value'),   # style
    Input('layer-switch-2d', 'value'),      # failles/séismes
    Input('zone-display-switch', 'value'),  # zones globe
    Input('view-switch', 'value'),          # "2D" ou "3D"
    Input('main-graph', 'hoverData')        # hover data (2D ou 3D)
)
def update_visuals(mag_range, map_style, layers_2d, zone_3d, view_mode, hover_data):
    """
    Met à jour l'histogramme et le graphique principal (2D ou 3D),
    selon le filtrage, la vue choisie et les couches cochées.
    """
    # Filtrage
    filtered_df = df[df['mag'].between(*mag_range)]

    # 1) Histogramme
    hist_fig = common_functions.create_magnitude_histogram(filtered_df)
    hist_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        plot_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF")
    )

    # 2) Vue 2D ou 3D ?
    if view_mode == "2D":
        # Créer la figure Mapbox
        main_fig = common_functions.create_earthquake_map(filtered_df, map_style)

        # Ajouter les failles si cochées
        if "failles" in layers_2d:
            main_fig = common_functions.add_fault_lines_mapbox(main_fig, tectonic_data)

        # Ajouter les séismes si cochés
        if "seismes" in layers_2d:
            main_fig.add_trace(go.Scattermapbox(
                lat=filtered_df['latitude'],
                lon=filtered_df['longitude'],
                mode='markers',
                marker=dict(size=8, color="#e74c3c", opacity=0.9),
                name="Séismes"
            ))

        # Si ni failles ni séismes cochés -> trace fictive
        if not layers_2d:
            main_fig.add_trace(go.Scattermapbox(
                lon=[0], lat=[0],
                mode='markers',
                marker=dict(size=1, color="rgba(0,0,0,0)"),
                name="(Aucune couche)",
                showlegend=True
            ))

        # Mise en forme
        main_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#2A2E3E",
            font=dict(color="#FFFFFF"),
            uirevision='map_update'
        )

    else:
        # "3D" : on utilise create_globe_figure
        main_fig = common_functions.create_globe_figure(filtered_df, globe_style=map_style)
        main_fig.update_layout(
            uirevision="globe_update",
            template="plotly_dark",
            paper_bgcolor="#2A2E3E",
            font=dict(color="#FFFFFF")
        )

        # Zones ressenties si "globe-zones" coché
        if 'globe-zones' in zone_3d and hover_data:
            lat_hover = hover_data['points'][0]['lat']
            lon_hover = hover_data['points'][0]['lon']
            hovered_point = filtered_df[
                (filtered_df['latitude'] == lat_hover) &
                (filtered_df['longitude'] == lon_hover)
            ]
            if not hovered_point.empty:
                mag_val = hovered_point['mag'].values[0]
                radius_km = 10 ** (0.5 * mag_val + 1)
                circle_coords = common_functions.create_geodesic_circle(lat_hover, lon_hover, radius_km)
                polygons = common_functions.split_polygon_at_dateline(circle_coords)
                for poly in polygons:
                    if len(poly) < 3:
                        continue
                    lat_poly = [p[0] for p in poly]
                    lon_poly = [p[1] for p in poly]
                    main_fig.add_trace(go.Scattergeo(
                        lat=lat_poly,
                        lon=lon_poly,
                        fill='toself',
                        fillcolor='rgba(0, 0, 255, 0.2)',
                        line=dict(color='blue'),
                        hoverinfo='skip',
                        name='Zone ressentie'
                    ))

    return hist_fig, main_fig
