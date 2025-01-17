import requests
from typing import Union

def fetch_earthquake_data(start_time: str, end_time: str, min_magnitude: Union[int, float]) -> None:
    """
    Télécharge les données de séismes au format CSV depuis l'API de l'USGS.
    
    :param start_time: Date de début (format ISO 8601, ex. "YYYY-MM-DD")
    :param end_time: Date de fin (format ISO 8601, ex. "YYYY-MM-DD")
    :param min_magnitude: Magnitude minimale des séismes à récupérer
    :return: None
    """
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "csv",
        "starttime": start_time,
        "endtime": end_time,
        "minmagnitude": min_magnitude
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        with open('data/raw/earthquake_data.csv', 'wb') as f:
            f.write(response.content)
        print("Data downloaded successfully.")
    else:
        print("Failed to download data.")


if __name__ == "__main__":
    fetch_earthquake_data("2024-01-01", "2024-11-26", 4.5)
