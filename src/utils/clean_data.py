import pandas as pd

def clean_earthquake_data():
    df = pd.read_csv('data/raw/earthquake_data.csv')
    # Handle missing values
    df = df.dropna(subset=['latitude', 'longitude', 'mag'])
    # Convert time to datetime
    df['time'] = pd.to_datetime(df['time'])
    # Save cleaned data
    df.to_csv('data/cleaned/earthquake_data_cleaned.csv', index=False)
    print("Data cleaned and saved.")

if __name__ == "__main__":
    clean_earthquake_data()
