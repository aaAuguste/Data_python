import pandas as pd
import plotly.graph_objects as go
from geopy.distance import distance as geopy_distance

def create_magnitude_histogram(df):
    """
    Crée un histogramme des magnitudes des séismes.
    """
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['mag'],
        marker_color='#3498db',  # Couleur bleue
        opacity=0.75
    ))
    fig.update_layout(
        title="Distribution des Magnitudes",
        xaxis_title="Magnitude",
        yaxis_title="Nombre d'événements",
        template="plotly_white",
        font=dict(family="Montserrat, Arial, sans-serif", size=14),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

def create_earthquake_map(df, map_style='open-street-map'):
    """
    Crée une figure Mapbox (sans séismes ni failles),
    simplement centrée sur la zone moyenne du df (si non vide).
    """
    fig = go.Figure()

    # Choix du style
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

    # Centrage et zoom
    if not df.empty:
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
    else:
        # Si DF vide, centrer sur (0,0)
        center_lat = 0
        center_lon = 0

    fig.update_layout(
        mapbox=dict(
            zoom=1,
            center={"lat": center_lat, "lon": center_lon}
        ),
        title="Carte des Séismes",
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(family="Montserrat, Arial, sans-serif", size=14)
    )
    return fig



def load_clean_data():
    """
    Charge les données nettoyées depuis un fichier CSV.
    """
    df = pd.read_csv('data/cleaned/earthquake_data_cleaned.csv')
    return df

def create_hover_circle(lat, lon, radius):
    """
    Crée un cercle pour représenter la zone ressentie autour du point.
    """
    return go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode="markers",
        marker=dict(size=radius * 3, color="rgba(0, 0, 255, 0.3)", opacity=0.5),
        hoverinfo="skip",
        name="Zone ressentie"
    )

def create_globe_figure(df_filtered, globe_style='open-street-map'):
    """
    Crée un globe (projection orthographique)
    en adaptant approximativement les couleurs land/ocean au style choisi.
    """
    land_color = "rgb(229,229,229)"
    ocean_color = "rgb(135,206,250)"
    if globe_style == 'carto-darkmatter':
        land_color = "rgb(40,40,40)"
        ocean_color = "rgb(30,30,30)"
    elif globe_style == 'carto-positron':
        land_color = "rgb(250,250,250)"
        ocean_color = "rgb(220,220,220)"
    elif globe_style == 'ocean-esri':
        land_color = "rgb(236,236,236)"
        ocean_color = "rgb(173,216,230)"
    elif globe_style == 'satellite-esri':
        land_color = "rgb(70,120,50)"
        ocean_color = "rgb(30,60,130)"

    fig = go.Figure()

    # Points sismiques
    fig.add_trace(go.Scattergeo(
        lat=df_filtered['latitude'],
        lon=df_filtered['longitude'],
        mode='markers',
        marker=dict(size=4, color='red', opacity=0.7),
        text=df_filtered['place'],
        hovertemplate="<b>Lieu:</b> %{text}<br>Lat:%{lat}, Lon:%{lon}<extra></extra>",
        name="Séismes"
    ))

    # Projection orthographique
    fig.update_geos(
        projection_type="orthographic",
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor=land_color,
        oceancolor=ocean_color,
        showocean=True
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#2A2E3E",
        plot_bgcolor="#2A2E3E",
        font=dict(color="#FFFFFF"),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        uirevision="globe_update",
        geo=dict(
            projection_scale=0.85
        )
    )
    return fig

def create_geodesic_circle(lat_c, lon_c, radius_km, n_points=72):
    """
    Construit un polygone (liste de (lat, lon)) formant un cercle géodésique
    (suivant la courbure de la Terre) de rayon `radius_km` autour de (lat_c, lon_c).
    """
    coords = []
    step = 360 / n_points
    for i in range(n_points):
        bearing = i * step
        pt = geopy_distance(kilometers=radius_km).destination((lat_c, lon_c), bearing)
        coords.append((pt.latitude, pt.longitude))
    # Boucler en revenant au premier point
    if coords:
        coords.append(coords[0])
    return coords

def split_polygon_at_dateline(coords):
    """
    Découpe la liste de points (lat, lon) en plusieurs polygones
    si l'on franchit ±180° de longitude. Évite les grandes lignes
    qui traversent la map ou le globe quand le cercle est très grand.
    
    Retourne une liste de polygones, chacun ne franchissant pas ±180°.
    """
    polygons = []
    if not coords:
        return polygons

    current_poly = [coords[0]]
    for i in range(1, len(coords)):
        lat_prev, lon_prev = current_poly[-1]
        lat_curr, lon_curr = coords[i]
        
        # Détection d'une "coupure" sur ±180° (antiméridien)
        if abs(lon_curr - lon_prev) > 180:
            polygons.append(current_poly[:])
            current_poly = [(lat_curr, lon_curr)]
        else:
            current_poly.append((lat_curr, lon_curr))
    
    if current_poly:
        polygons.append(current_poly)
    return polygons

def add_fault_lines_mapbox(fig, tectonic_data):
    """
    Construit un unique Scattermapbox contenant toutes les failles.
    Chaque segment est séparé par None, ce qui permet à Plotly
    de tracer plusieurs lignes dans un seul trace.
    """
    all_lons = []
    all_lats = []

    for feature in tectonic_data["features"]:
        geometry = feature["geometry"]
        if geometry["type"] == "LineString":
            coords = geometry["coordinates"]  # liste de [lon, lat]
            for c in coords:
                all_lons.append(c[0])
                all_lats.append(c[1])
            # Séparation entre segments
            all_lons.append(None)
            all_lats.append(None)

        elif geometry["type"] == "MultiLineString":
            for line_coords in geometry["coordinates"]:
                # line_coords : liste de [lon, lat]
                for c in line_coords:
                    all_lons.append(c[0])
                    all_lats.append(c[1])
                all_lons.append(None)
                all_lats.append(None)

    # Retirer éventuellement le dernier None
    if all_lons and all_lons[-1] is None:
        all_lons.pop()
        all_lats.pop()

    # On ajoute UNE SEULE trace en mode "lines"
    fig.add_trace(go.Scattermapbox(
        lon=all_lons,
        lat=all_lats,
        mode="lines",
        line=dict(color="orange", width=2),
        name="Failles tectoniques"
    ))
    return fig
