mport plotly.express as px
import pandas as pd

def create_magnitude_histogram(df):
    fig = px.histogram(df, x='mag', nbins=50, title='Earthquake Magnitude Distribution')
    fig.update_layout(xaxis_title='Magnitude', yaxis_title='Count')
    return fig
def load_clean_data():
    df = pd.read_csv('data/cleaned/earthquake_data_cleaned.csv')
    return df