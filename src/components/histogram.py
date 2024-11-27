from dash import dcc, html
from src.utils import common_functions as cf

df = cf.load_clean_data()

histogram_fig = cf.create_magnitude_histogram(df)

histogram_component = html.Div([
    dcc.Graph(figure=histogram_fig)
])


from dash import dcc, html, Input, Output, callback
from ..utils import common_functions
from ..app import app  # Import the app instance

df = common_functions.load_clean_data()

# Create the histogram figure with initial data
histogram_fig = common_functions.create_magnitude_histogram(df)

# Create the histogram component
histogram_component = html.Div([
    dcc.Graph(id='histogram', figure=histogram_fig),
    dcc.RangeSlider(
        id='magnitude-slider',
        min=df['mag'].min(),
        max=df['mag'].max(),
        step=0.1,
        value=[df['mag'].min(), df['mag'].max()],
        marks={str(mag): str(mag) for mag in range(int(df['mag'].min()), int(df['mag'].max())+1)}
    )
])

# Define the callback function
@app.callback(
    Output('histogram', 'figure'),
    Input('magnitude-slider', 'value')
)
def update_histogram(magnitude_range):
    filtered_df = df[df['mag'].between(magnitude_range[0], magnitude_range[1])]
    fig = common_functions.create_magnitude_histogram(filtered_df)
    return fig
