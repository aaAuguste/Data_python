import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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
    Crée une carte interactive des séismes.
    """
    C = -2.5
    df['radius'] = df['mag'].apply(lambda M: 10 ** (0.5 * M + C))

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=df['latitude'],
        lon=df['longitude'],
        mode="markers",
        marker=dict(size=8, color="#e74c3c", opacity=0.9),
        hovertemplate=(
            "<b>Lieu :</b> %{hovertext}<br>"
            "<b>Magnitude :</b> %{customdata[0]}<br>"
            "<b>Zone ressentie :</b> %{customdata[1]} km<extra></extra>"
        ),
        hovertext=df['place'],
        customdata=np.stack((df['mag'], np.round(df['radius'], 1)), axis=-1),
        name="Séismes"
    ))

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

    fig.update_layout(
        mapbox=dict(
            zoom=1,
            center={"lat": df['latitude'].mean(), "lon": df['longitude'].mean()}
        ),
        title="Carte des Séismes avec Zones Ressenties au Survol",
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
