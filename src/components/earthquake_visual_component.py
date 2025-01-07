from dash import dcc, html, Input, Output, State, callback
from ..utils import common_functions
import plotly.graph_objects as go
import requests
import json

# URL du GeoJSON des frontières tectoniques
geojson_url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json"
response = requests.get(geojson_url)
tectonic_data = json.loads(response.text)

# Chargement du DataFrame des séismes depuis une fonction utilitaire
df = common_functions.load_clean_data()

# Calcul des valeurs de référence pour la plage de magnitude
mag_min = df['mag'].min()
mag_max = df['mag'].max()

# Quelques statistiques descriptives (total, moyenne, min, max)
total_seismes = len(df)
magnitude_moyenne = round(df['mag'].mean(), 2)
magnitude_max_ = df['mag'].max()
magnitude_min_ = df['mag'].min()

# Composant RangeSlider pour sélectionner la plage de magnitudes
magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=mag_min,
    max=mag_max,
    step=0.1,
    value=[mag_min, mag_max],
    marks={str(int(m)): str(int(m)) for m in range(int(mag_min), int(mag_max) + 1)},
    tooltip={"placement": "bottom", "always_visible": True}
)

# Dropdown pour choisir le style de la carte
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
    style={"color": "#000"}  # Style inline, en camelCase si besoin
)

# Bouton pour afficher/masquer le menu latéral
menu_toggle_btn = html.Button(
    "☰ Menu",
    id="menu-toggle-btn",
    n_clicks=0,
    className="menu-toggle-btn"  # défini dans style.css
)

# Contenu interne de la sidebar
sidebar_content = html.Div(
    id="sidebar-content",
    children=[
        html.H2("Menu"),
        # Contrôles de l'histogramme (RangeSlider)
        html.Div([
            html.Label("Contrôles de l'histogramme"),
            magnitude_selection
        ]),
        # Contrôles de la carte (Dropdown)
        html.Div([
            html.Label("Contrôles de la carte"),
            map_style_dropdown
        ]),
        html.Hr(),
        # Bloc d'infographies (KPIs)
        html.Div([
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
        ])
    ]
)

# Conteneur global de la sidebar (ouverte par défaut)
sidebar = html.Div(
    id="sidebar",
    children=[sidebar_content],
    className="sidebar-open"
)

# Conteneur principal (ouvert par défaut)
main_content = html.Div(
    id="main-content",
    className="content-open",
    children=[
        # Bouton pour afficher la sidebar
        html.Div(menu_toggle_btn),
        
        # Histogramme
        html.Div(
            dcc.Graph(id='histogram', className="graph-container")
        ),

        # Map 2D + checklist
        html.Div(
            children=[
                dcc.Graph(
                    id='map',
                    className="graph-container",
                    config={'scrollZoom': True}
                ),
                dcc.Checklist(
                    id="layer-switch-2d",
                    options=[
                        {"label": "Failles tectoniques", "value": "failles"},
                        {"label": "Séismes", "value": "seismes"}
                    ],
                    value=["failles", "seismes"],  # tout coché par défaut
                    style={"color": "#fff"}
                )
            ],
            className="my-map-container"
        ),

        # Globe 3D
        html.Div([
            html.H3("Globe 3D (projection orthographique)"),
            dcc.Graph(id='globe', className="graph-container"),
            dcc.Checklist(
                id="zone-display-switch",
                options=[{'label': 'Afficher zones sur le Globe', 'value': 'globe-zones'}],
                value=[],
                style={"color": "#fff"}
            )
            ], className="my-3d-globe-container")
    ])

# Assemblage final : sidebar + contenu
earthquake_component = html.Div(
    children=[sidebar, main_content],
    className="earthquake-container"
)

def create_earthquake_map(df, map_style='open-street-map'):
    """
    Crée une figure Mapbox vide (pas de séismes), configurée selon `map_style`.
    """
    fig = go.Figure()
    # Choix du style de la carte
    if map_style in ['open-street-map', 'carto-positron', 'carto-darkmatter', 'white-bg']:
        fig.update_layout(mapbox_style=map_style)
    elif map_style == 'satellite-esri':
        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[{
                "below": "traces",
                "sourcetype": "raster",
                "source": [
                    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                ]
            }]
        )
    elif map_style == 'ocean-esri':
        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[{
                "below": "traces",
                "sourcetype": "raster",
                "source": [
                    "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
                ]
            }]
        )

    # Centrage / Zoom
    if not df.empty:
        fig.update_layout(
            mapbox=dict(
                zoom=1,
                center={
                    "lat": df['latitude'].mean(),
                    "lon": df['longitude'].mean()
                }
            ),
            title="Carte des Séismes",
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Montserrat, Arial, sans-serif", size=14)
        )
    else:
        # Si DF vide, centrage arbitraire
        fig.update_layout(
            mapbox=dict(
                zoom=1,
                center={"lat": 0, "lon": 0}
            ),
            title="Carte (Pas de données)",
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Montserrat, Arial, sans-serif", size=14)
        )
    return fig

###############################################################################
# Callback : affichage de la sidebar
###############################################################################
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


###############################################################################
# Callback : mise à jour des trois figures (histogramme, carte 2D, globe 3D)
###############################################################################
@callback(
    Output('histogram', 'figure'),
    Output('map', 'figure'),
    Output('globe', 'figure'),
    Input('magnitude-slider', 'value'),   
    Input('map-style-dropdown', 'value'), 
    Input('layer-switch-2d', 'value'),    
    Input('map', 'hoverData'),           
    Input('globe', 'hoverData'),         
    Input('zone-display-switch', 'value')
)
def update_visuals(mag_range, map_style, layers_checked,
                   hover_data_map, hover_data_globe,
                   zone_switch):

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

    # 2) Carte 2D "vide" (pas de failles, pas de séismes)
    map_fig = create_earthquake_map(filtered_df, map_style=map_style)

    # Si "failles" coché -> ajout trace unique "Failles tectoniques"
    if "failles" in layers_checked:
        map_fig = common_functions.add_fault_lines_mapbox(map_fig, tectonic_data)

    # Si "seismes" coché -> ajout du scatter de séismes
    if "seismes" in layers_checked:
        map_fig.add_trace(go.Scattermapbox(
            lat=filtered_df['latitude'],
            lon=filtered_df['longitude'],
            mode='markers',
            marker=dict(size=8, color="#e74c3c", opacity=0.9),
            name="Séismes",
            showlegend=True
        ))

    # Si ni failles ni séismes cochés -> On ajoute une trace "fictive"
    if not layers_checked:
        map_fig.add_trace(go.Scattermapbox(
            lon=[0],
            lat=[0],
            mode='markers',
            marker=dict(size=1, color="rgba(0,0,0,0)"),
            name="(Aucune couche)",
            showlegend=True
        ))

    # Layout map
    map_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF"),
        uirevision='map_update'
    )

    # 3) Globe 3D
    globe_fig = common_functions.create_globe_figure(filtered_df, globe_style=map_style)
    globe_fig.update_layout(uirevision="globe_update")

    if 'globe-zones' in zone_switch and hover_data_globe:
        lat_hover = hover_data_globe['points'][0]['lat']
        lon_hover = hover_data_globe['points'][0]['lon']
        hovered_point = filtered_df[
            (filtered_df['latitude'] == lat_hover) &
            (filtered_df['longitude'] == lon_hover)
        ]
        if not hovered_point.empty:
            mag_val = hovered_point['mag'].values[0]
            radius_km = 10 ** (0.5 * mag_val + 1)
            circle_coords = common_functions.create_geodesic_circle(lat_hover, lon_hover, radius_km)
            polygons_globe = common_functions.split_polygon_at_dateline(circle_coords)
            for poly in polygons_globe:
                # Éviter d'ajouter des polygones vides ou trop courts
                if len(poly) < 3:
                    continue
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
