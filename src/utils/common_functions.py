import plotly.express as px
import pandas as pd

import plotly.graph_objects as go

def create_magnitude_histogram(df):
    fig = go.Figure()

    # Ajout de données
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

    return fig
def load_clean_data():
    df = pd.read_csv('data/cleaned/earthquake_data_cleaned.csv')
    return df


def create_earthquake_map(df):
    """
    Crée une carte interactive des séismes avec des tailles de points adaptées
    au zoom et à la magnitude.
    """
    # Ajustez la taille des points en fonction de la magnitude
    df['size'] = df['mag'] * 10

    # Créez la carte avec scatter_mapbox
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        size="size",  
        color="mag",  
        hover_name="place",  
        hover_data={"mag": True, "size": False},  
        mapbox_style="carto-positron",  
        zoom=1,  
    )

    # Mettez à jour le layout pour activer l'adaptation au zoom
    fig.update_layout(
        title="Carte des Séismes",
        font=dict(family="Arial, sans-serif", size=1),
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        mapbox=dict(
            zoom=1,  
            center={"lat": df['latitude'].mean(), "lon": df['longitude'].mean()}  
        )
    )

    # Ajouter des tailles de point dynamiques basées sur le zoom (optionnelle)
    fig.update_traces(
        marker=dict(
            sizemode='area',
            sizeref=max(df['size']) / (20.0 ** 2), 
            sizemin=5  # Taille minimale des points
        )
    )

    
    fig.update_layout(
        title="Carte des Séismes",
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig
