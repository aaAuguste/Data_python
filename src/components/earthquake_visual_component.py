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
    # marks : étiquettes visibles sur le slider pour chaque magnitude entière
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
    value='open-street-map',  # valeur par défaut
    clearable=False,
    # Important pour un thème sombre : on force la couleur du texte en noir
    style={"color": "#000"}
)

# Bouton pour afficher/masquer le menu latéral
menu_toggle_btn = html.Button(
    "☰ Menu",               # texte à l'intérieur du bouton
    id="menu-toggle-btn",   # identifiant pour le callback
    n_clicks=0,             # initialisation du compteur de clics
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

# Définition du style CSS pour la sidebar ouverte et fermée
# On gère la transition de largeur pour animer l'ouverture/fermeture
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

# Style du contenu principal, lorsqu'on ouvre ou ferme la sidebar
CONTENT_STYLE_OPEN = {
    "margin-left": "320px",
    "padding": "20px"
}
CONTENT_STYLE_CLOSED = {
    "margin-left": "20px",
    "padding": "20px"
}

# Contenu interne de la sidebar
sidebar_content = html.Div(
    id="sidebar-content",
    children=[
        html.H2("Menu", style={"margin-bottom": "30px", "text-align": "center"}),

        # Contrôles de l'histogramme (RangeSlider)
        html.Div([
            html.Label(
                "Contrôles de l'histogramme", 
                style={"font-weight": "bold", "color": "#ffffff", "margin-bottom": "10px"}
            ),
            magnitude_selection
        ], style={"margin-bottom": "40px"}),

        # Contrôles de la carte (Dropdown)
        html.Div([
            html.Label(
                "Contrôles de la carte",
                style={"font-weight": "bold", "color": "#ffffff", "margin-bottom": "10px"}
            ),
            map_style_dropdown
        ], style={"margin-bottom": "40px"}),

        html.Hr(style={"border": "1px solid #ffffff"}),

        # Bloc d'infographies (KPIs) : total séismes, magnitude moyenne, etc.
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

# Conteneur global de la sidebar
sidebar = html.Div(
    id="sidebar",
    children=[sidebar_content],
    style=SIDEBAR_OPEN  # Par défaut, sidebar ouverte
)

# Conteneur principal, qui inclut :
#  - Un bouton pour afficher le menu
#  - Le graphique d'histogramme
#  - La carte 2D
#  - Le globe 3D
main_content = html.Div(
    id="main-content",
    children=[
        # Bouton pour afficher la sidebar
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

        # Globe 3D
        html.Div([
            html.H3("Globe 3D (projection orthographique)", style={"margin-bottom": "20px"}),

            html.Div([
                # Case à cocher pour activer/désactiver l’affichage des zones sur le globe
                dcc.Checklist(
                    id="zone-display-switch",
                    options=[{'label': 'Afficher zones sur le Globe', 'value': 'globe-zones'}],
                    value=[],  # Par défaut décoché
                    style={"color": "#fff", "margin-bottom": "10px"}
                ),
                # Graphique (figure) du globe
                dcc.Graph(id='globe', className="graph-container")
            ], style={"padding": "10px", "background-color": "#2A2E3E", "border-radius": "10px"})
        ], style={"margin-top": "20px"})
    ],
    style=CONTENT_STYLE_OPEN  # Par défaut, on laisse la place pour la sidebar
)

# Assemblage final : sidebar + contenu
earthquake_component = html.Div(
    children=[sidebar, main_content],
    style={
        "position": "relative",
        "height": "100vh",
        "background-color": "transparent"
    }
)

###############################################################################
# Callback : affichage de la sidebar
###############################################################################
@callback(
    Output("sidebar", "style"),
    Output("main-content", "style"),
    Input("menu-toggle-btn", "n_clicks"),
    State("sidebar", "style"),
    State("main-content", "style"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, sidebar_style, content_style):
    """
    Au clic sur le bouton menu-toggle-btn :
    - Si la sidebar est ouverte, on la ferme et on applique un style "CONTENT_STYLE_CLOSED" au contenu
    - Sinon, on l'ouvre et on applique "CONTENT_STYLE_OPEN"
    """
    if not sidebar_style:
        return SIDEBAR_OPEN, CONTENT_STYLE_OPEN

    # Détection de l'état : si width=300px, la sidebar est considérée comme ouverte
    if sidebar_style.get("width") == "300px":
        return SIDEBAR_CLOSED, CONTENT_STYLE_CLOSED
    else:
        return SIDEBAR_OPEN, CONTENT_STYLE_OPEN


###############################################################################
# Callback : mise à jour des trois figures (histogramme, carte 2D, globe 3D)
###############################################################################
@callback(
    Output('histogram', 'figure'),
    Output('map', 'figure'),
    Output('globe', 'figure'),
    Input('magnitude-slider', 'value'),    # plage de magnitudes sélectionnée
    Input('map-style-dropdown', 'value'),  # style de carte choisi
    Input('map', 'hoverData'),             # interaction hover sur la carte 2D
    Input('globe', 'hoverData'),           # interaction hover sur le globe 3D
    Input('zone-display-switch', 'value')  # activation de l'affichage des zones (checklist)
)
def update_visuals(mag_range, map_style, hover_data_map, hover_data_globe, zone_switch):
    """
    Met à jour les trois visualisations en fonction de :
      - la plage de magnitude sélectionnée
      - le style de carte (2D)
      - l'interaction hover (carte 2D et globe 3D)
      - le switch pour afficher les zones sur le globe
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
        uirevision='map_update'  # évite le recentrage de la carte lors des callbacks
    )

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

    # 3) Globe 3D
    globe_fig = common_functions.create_globe_figure(filtered_df, globe_style=map_style)
    globe_fig.update_layout(uirevision="globe_update")  # maintient la position du globe

    # Si l'affichage des zones ("globe-zones") est activé ET qu'un point est hover sur le globe
    if 'globe-zones' in zone_switch and hover_data_globe:
        lat_hover = hover_data_globe['points'][0]['lat']
        lon_hover = hover_data_globe['points'][0]['lon']
        hovered_point = filtered_df[
            (filtered_df['latitude'] == lat_hover) & (filtered_df['longitude'] == lon_hover)
        ]
        if not hovered_point.empty:
            # Calcul du rayon en km à partir de la magnitude
            # Formule classique : rayon = 10^(0.5 * mag + 1)
            mag_val = hovered_point['mag'].values[0]
            radius_km = 10 ** (0.5 * mag_val + 1)

            # Génère un "cercle" géodésique autour du point cliqué
            circle_coords = common_functions.create_geodesic_circle(lat_hover, lon_hover, radius_km)
            # Découpe si le cercle franchit la ligne de changement de date (±180°)
            polygons_globe = common_functions.split_polygon_at_dateline(circle_coords)

            # Ajout du polygone sur le globe (comme une ou plusieurs traces)
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
