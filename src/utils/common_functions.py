import plotly.express as px
import pandas as pd

def create_magnitude_histogram(df):
    fig = px.histogram(df, x='mag', nbins=50, title='Earthquake Magnitude Distribution')
    fig.update_layout(xaxis_title='Magnitude', yaxis_title='Count')
    return fig
def load_clean_data():
    df = pd.read_csv('data/cleaned/earthquake_data_cleaned.csv')
    return df
def create_earthquake_map(df):
    fig = px.scatter_geo(df,
                         lat='latitude',
                         lon='longitude',
                         hover_name='place',
                         size='mag',
                         color='depth',
                         color_continuous_scale='Viridis',
                         title='Global Earthquake Locations')
    fig.update_layout(geo=dict(showland=True))
    return fig