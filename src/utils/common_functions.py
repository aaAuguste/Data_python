import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def create_magnitude_histogram(df):
    """
    Crée un histogramme des magnitudes des séismes.
    """
    fig = go.Figure()

    # Ajout de données pour l'histogramme
    fig.add_trace(go.Histogram(
        x=df['mag'],
        marker_color='blue',
        opacity=0.75
    ))

    # Mise en page stylisée
    fig.update_layout(
        title="Distribution des Magnitudes",
        xaxis_title="Magnitude",
        yaxis_title="Nombre d'événements",
        template="plotly_white",
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

def load_clean_data():
    """
    Charge les données nettoyées depuis un fichier CSV.
    """
    df = pd.read_csv('data/cleaned/earthquake_data_cleaned.csv')
    return df

def create_earthquake_map(df, map_style='open-street-map'):
    import plotly.express as px

    df['size'] = df['mag'] * 10
    
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        size="size",
        color="mag",
        hover_name="place",
        hover_data={"mag": True, "size": False},
        zoom=1,
        center={"lat": df['latitude'].mean(), "lon": df['longitude'].mean()}
    )
    
    # Gestion des styles
    # On va utiliser une logique conditionnelle :
    # - Si map_style est un des styles "natifs" (open-street-map, carto-positron, carto-darkmatter, white-bg),
    #   on applique simplement ce style.
    # - Si map_style == 'satellite-esri', on met white-bg + couche raster Esri.
    # - Si map_style == 'oceans', on met open-street-map + couche OpenSeaMap.
    
    if map_style in ['open-street-map', 'carto-positron', 'carto-darkmatter', 'white-bg']:
        # Styles par défaut supportés par Plotly sans token
        fig.update_layout(
            mapbox_style=map_style,
            title="Carte des Séismes",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            uirevision=map_style
        )
    elif map_style == 'satellite-esri':
        # Style satellite basé sur Esri World Imagery
        fig.update_layout(
            mapbox_style="white-bg",
            title="Carte des Séismes (Satellite)",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            uirevision=map_style,
            mapbox={
                "layers": [
                    {
                        "below": "traces",
                        "sourcetype": "raster",
                        "source": [
                            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                ]
            }
        )
    elif map_style == 'oceans':
        # Style océan basé sur OpenSeaMap au-dessus d'open-street-map
        fig.update_layout(
            mapbox_style="open-street-map",
            title="Carte des Séismes (Océans détaillés)",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            uirevision=map_style,
            mapbox={
                "layers": [
                    {
                        "below": "traces",
                        "sourcetype": "raster",
                        "source": ["https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"]
                    }
                ]
            }
        )
    elif map_style == 'ocean-esri':
        fig.update_layout(
            mapbox_style="white-bg",
            title="Carte des Séismes (Océans Esri)",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            uirevision=map_style,
            mapbox={
                "layers": [
                    {
                        "below": "traces",
                        "sourcetype": "raster",
                        "source": [
                            "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                ]
            }
        )


    fig.update_traces(
        marker=dict(
            sizemode='area',
            sizeref=max(df['size']) / (20.0 ** 2),
            sizemin=5
        )
    )

    return fig
