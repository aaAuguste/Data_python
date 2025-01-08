from src.app import app
from src.pages import home

app.layout = home.layout

if __name__ == '__main__':
    app.run_server(debug=True)
    