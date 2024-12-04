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
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="mag",
        size="mag",
        hover_name="place",
        mapbox_style="carto-positron",  # Style de la carte
        zoom=3
    )

    fig.update_layout(
        title="Carte des Séismes",
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig
