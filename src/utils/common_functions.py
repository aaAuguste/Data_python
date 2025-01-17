import pandas as pd
import plotly.graph_objects as go
from geopy.distance import distance as geopy_distance
from typing import List, Tuple,Any, Union

def create_magnitude_histogram(df: pd.DataFrame) -> go.Figure:
    """
    Crée un histogramme des magnitudes des séismes.
    Args:
        df: DataFrame contenant une colonne 'mag' pour les magnitudes.
    Returns:
        Un objet `go.Figure` représentant l'histogramme.
    """
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df['mag'],
        marker_color='#3498db',
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

def create_earthquake_map(df: pd.DataFrame, map_style: str = 'open-street-map') -> go.Figure:
    """
    Crée une figure Mapbox centrée sur la zone moyenne du DataFrame.
    Args:
        df: DataFrame contenant les colonnes 'latitude' et 'longitude'.
        map_style: Style de la carte ('open-street-map', 'carto-positron', etc.).
    Returns:
        Un objet `go.Figure` représentant la carte.
    """
    fig = go.Figure()
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
    if not df.empty:
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
    else:
        center_lat, center_lon = 0, 0
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

def load_clean_data() -> pd.DataFrame:
    """
    Charge les données nettoyées depuis un fichier CSV.
    Returns:
        DataFrame contenant les données nettoyées.
    """
    return pd.read_csv('data/cleaned/earthquake_data_cleaned.csv')

def create_hover_circle(lat: float, lon: float, radius: float) -> go.Scattermapbox:
    """
    Crée un cercle pour représenter la zone ressentie autour d'un point.
    Args:
        lat: Latitude du centre du cercle.
        lon: Longitude du centre du cercle.
        radius: Rayon du cercle.
    Returns:
        Un objet `Scattermapbox` représentant le cercle.
    """
    return go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode="markers",
        marker=dict(size=radius * 3, color="rgba(0, 0, 255, 0.3)", opacity=0.5),
        hoverinfo="skip",
        name="Zone ressentie"
    )

def create_globe_figure(df_filtered: pd.DataFrame, globe_style: str = 'open-street-map') -> go.Figure:
    """
    Crée un globe (projection orthographique) avec les séismes.
    Args:
        df_filtered: DataFrame contenant les colonnes 'latitude', 'longitude', 'place', et 'mag'.
        globe_style: Style du globe.
    Returns:
        Un objet `go.Figure` représentant le globe.
    """
    land_color, ocean_color = "rgb(229,229,229)", "rgb(135,206,250)"
    if globe_style == 'carto-darkmatter':
        land_color, ocean_color = "rgb(40,40,40)", "rgb(30,30,30)"
    elif globe_style == 'carto-positron':
        land_color, ocean_color = "rgb(250,250,250)", "rgb(220,220,220)"
    elif globe_style == 'ocean-esri':
        land_color, ocean_color = "rgb(236,236,236)", "rgb(173,216,230)"
    elif globe_style == 'satellite-esri':
        land_color, ocean_color = "rgb(70,120,50)", "rgb(30,60,130)"
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=df_filtered['latitude'],
        lon=df_filtered['longitude'],
        mode='markers',
        marker=dict(size=4, color='red', opacity=0.7),
        customdata=df_filtered[['place', 'mag']].values,
        hovertemplate=(
            "<b>Lieu:</b> %{customdata[0]}<br>"
            "<b>Magnitude:</b> %{customdata[1]}<br>"
            "Latitude: %{lat}<br>"
            "Longitude: %{lon}<extra></extra>"
        ),
        name="Séismes"
    ))
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
        geo=dict(projection_scale=0.85)
    )
    return fig

def create_geodesic_circle(lat_c: float, lon_c: float, radius_km: float, n_points: int = 72) -> List[Tuple[float, float]]:
    """
    Construit un polygone formant un cercle géodésique autour d'un point.
    Args:
        lat_c: Latitude du centre du cercle.
        lon_c: Longitude du centre du cercle.
        radius_km: Rayon du cercle en kilomètres.
        n_points: Nombre de points à utiliser pour construire le cercle.
    Returns:
        Liste de tuples (latitude, longitude) représentant le cercle.
    """
    coords = []
    step = 360 / n_points
    for i in range(n_points):
        bearing = i * step
        pt = geopy_distance(kilometers=radius_km).destination((lat_c, lon_c), bearing)
        coords.append((pt.latitude, pt.longitude))
    if coords:
        coords.append(coords[0])
    return coords

def split_polygon_at_dateline(coords: List[Tuple[float, float]]) -> List[List[Tuple[float, float]]]:
    """
    Découpe une liste de points en plusieurs polygones si elle traverse le méridien ±180°.
    Args:
        coords: Liste de tuples (latitude, longitude) représentant un polygone.
    Returns:
        Liste de polygones ne traversant pas le méridien ±180°.
    """
    polygons: list[Any] = []
    if not coords:
        return polygons
    current_poly = [coords[0]]
    for i in range(1, len(coords)):
        lat_prev, lon_prev = current_poly[-1]
        lat_curr, lon_curr = coords[i]
        if abs(lon_curr - lon_prev) > 180:
            polygons.append(current_poly[:])
            current_poly = [(lat_curr, lon_curr)]
        else:
            current_poly.append((lat_curr, lon_curr))
    if current_poly:
        polygons.append(current_poly)
    return polygons

def add_fault_lines_mapbox(fig: go.Figure, tectonic_data: dict) -> go.Figure:
    """
    Ajoute des failles tectoniques à une figure Mapbox.
    Args:
        fig: Objet `go.Figure` représentant une carte.
        tectonic_data: Données GeoJSON des failles tectoniques.
    Returns:
        La figure modifiée avec les failles tectoniques.
    """
    all_lons = []
    all_lats = []
    for feature in tectonic_data["features"]:
        geometry = feature["geometry"]
        if geometry["type"] == "LineString":
            coords = geometry["coordinates"]
            for c in coords:
                all_lons.append(c[0])
                all_lats.append(c[1])
            all_lons.append(None)
            all_lats.append(None)
        elif geometry["type"] == "MultiLineString":
            for line_coords in geometry["coordinates"]:
                for c in line_coords:
                    all_lons.append(c[0])
                    all_lats.append(c[1])
                all_lons.append(None)
                all_lats.append(None)
    if all_lons and all_lons[-1] is None:
        all_lons.pop()
        all_lats.pop()
    fig.add_trace(go.Scattermapbox(
        lon=all_lons,
        lat=all_lats,
        mode="lines",
        line=dict(color="orange", width=2),
        name="Failles tectoniques"
    ))
    return fig
