from dash import dcc, html, Input, Output, State, callback
from ..utils import common_functions
import plotly.graph_objects as go

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
    min=mag_min,  # valeur minimale
    max=mag_max,  # valeur maximale
    step=0.1,     # pas de 0.1
    value=[mag_min, mag_max],  # plage de sélection initiale
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
    # On évite inline style, ou on le met en camelCase si besoin
    style={"color": "#000"}
)

# Bouton pour afficher/masquer le menu latéral
menu_toggle_btn = html.Button(
    "☰ Menu",
    id="menu-toggle-btn",
    n_clicks=0,
    className="menu-toggle-btn"  # On applique la classe CSS .menu-toggle-btn
)

# Contenu interne de la sidebar
sidebar_content = html.Div(
    id="sidebar-content",
    children=[
        html.H2("Menu"),  # Les styles sur <h2> sont dans style.css

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

        # Bloc d'infographies (KPIs) : total séismes, magnitude moyenne, etc.
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

# Conteneur global de la sidebar
# On utilise .sidebar-open (largeur=300px) par défaut
sidebar = html.Div(
    id="sidebar",
    children=[sidebar_content],
    className="sidebar-open"  
)

# Conteneur principal (on utilise .content-open pour laisser de la place)
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

        # Carte (2D)
        html.Div(
            dcc.Graph(id='map', className="graph-container", config={'scrollZoom': True})
        ),

        # Globe 3D
        html.Div([
            html.H3("Globe 3D (projection orthographique)"),

            html.Div([
                # Case à cocher pour activer/désactiver l’affichage des zones sur le globe
                dcc.Checklist(
                    id="zone-display-switch",
                    options=[{'label': 'Afficher zones sur le Globe', 'value': 'globe-zones'}],
                    value=[],
                    style={"color": "#fff"}  # Ça peut rester, c'est du camelCase
                ),
                # Graphique (figure) du globe
                dcc.Graph(id='globe', className="graph-container")
            ], className="my-3d-globe-container")
        ])
    ]
)

# Assemblage final : sidebar + contenu, dans un conteneur global
earthquake_component = html.Div(
    children=[sidebar, main_content],
    className="earthquake-container"
)

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
    Input('map', 'hoverData'),
    Input('globe', 'hoverData'),
    Input('zone-display-switch', 'value')
)
def update_visuals(mag_range, map_style, hover_data_map, hover_data_globe, zone_switch):
    """
    Met à jour les trois visualisations :
      - Histogramme des magnitudes
      - Carte 2D (Scattermapbox)
      - Globe 3D (Scattergeo orthographique)
    """
    # Filtrage du DataFrame sur la plage de magnitudes choisie
    filtered_df = df[df['mag'].between(*mag_range)]

    # 1) Histogramme
    hist_fig = common_functions.create_magnitude_histogram(filtered_df)
    hist_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        plot_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF")
    )

    # 2) Carte 2D
    map_fig = common_functions.create_earthquake_map(filtered_df, map_style=map_style)
    map_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF"),
        uirevision='map_update'
    )

    # 3) Globe 3D
    globe_fig = common_functions.create_globe_figure(filtered_df, globe_style=map_style)
    globe_fig.update_layout(uirevision="globe_update")

    # Gérer l'affichage des "zones ressenties" si coché
    if 'globe-zones' in zone_switch and hover_data_globe:
        lat_hover = hover_data_globe['points'][0]['lat']
        lon_hover = hover_data_globe['points'][0]['lon']
        hovered_point = filtered_df[
            (filtered_df['latitude'] == lat_hover) & (filtered_df['longitude'] == lon_hover)
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
