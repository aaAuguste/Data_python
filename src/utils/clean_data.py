import pandas as pd

def clean_earthquake_data() -> None:
    """
    Lit les données de séismes depuis un fichier CSV, effectue un nettoyage
    (gestion des valeurs manquantes, conversion de date/heure) et enregistre
    les données nettoyées dans un nouveau fichier CSV.

    :return: None
    """
    df: pd.DataFrame = pd.read_csv('data/raw/earthquake_data.csv')
    # Gérer les valeurs manquantes
    df = df.dropna(subset=['latitude', 'longitude', 'mag'])
    # Convertir la colonne 'time' en datetime
    df['time'] = pd.to_datetime(df['time'])
    # Enregistrer les données nettoyées
    df.to_csv('data/cleaned/earthquake_data_cleaned.csv', index=False)
    print("Data cleaned and saved.")

if __name__ == "__main__":
    clean_earthquake_data()
