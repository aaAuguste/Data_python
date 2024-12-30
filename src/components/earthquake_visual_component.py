from dash import dcc, html, Input, Output, State, callback
from ..utils import common_functions
from ..app import app
import pandas as pd
import plotly.express as px

# Chargement des données
df = common_functions.load_clean_data()

# Composants : RangeSlider, Dropdown
magnitude_selection = dcc.RangeSlider(
    id='magnitude-slider',
    min=df['mag'].min(),
    max=df['mag'].max(),
    step=0.1,
    value=[df['mag'].min(), df['mag'].max()],
    marks={str(int(mag)): str(int(mag)) for mag in range(int(df['mag'].min()), int(df['mag'].max()) + 1)},
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
    style={"color": "#000"}  # texte en noir pour le dropdown
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

# Bouton pour toggler la sidebar
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

# Contenu de la sidebar
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
        ], style={"margin-bottom": "40px"})
    ],
    style={"display": "block"}
)

# La sidebar (div) par défaut "ouverte"
sidebar = html.Div(
    id="sidebar",
    children=[sidebar_content],
    style=SIDEBAR_OPEN
)

# Contenu principal (histogram + map)
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
        ])
    ],
    style=CONTENT_STYLE_OPEN
)

# On assemble tout
earthquake_component = html.Div(
    children=[sidebar, main_content],
    style={
        "position": "relative",
        "height": "100vh",  # occupe toute la hauteur
        "background-color": "#1B2033"  # fond global sombre
    }
)

# Callback pour toggler la sidebar
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

# Callback principal
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
    # Style sombre
    hist_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        plot_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF")
    )

    map_fig = common_functions.create_earthquake_map(filtered_df, map_style=map_style)
    map_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF"),
        uirevision='map_update'
    )

    # Survol point
    if hover_data:
        lat_hover = hover_data['points'][0]['lat']
        lon_hover = hover_data['points'][0]['lon']
        hovered_point = filtered_df[
            (filtered_df['latitude'] == lat_hover) & (filtered_df['longitude'] == lon_hover)
        ]
        if not hovered_point.empty:
            mag_hover = hovered_point['mag'].values[0]
            radius = 10 ** (0.5 * mag_hover + 1)
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
            map_fig.add_trace(hover_circle.data[0])

    return hist_fig, map_fig
