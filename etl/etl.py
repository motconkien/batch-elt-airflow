import requests
import pandas as pd 
import os 
import json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert
import psycopg2
from dotenv import load_dotenv

load_dotenv()


CURRENT_API_ENDPOINT = 'https://api.openweathermap.org/data/2.5/weather'
HOURLY_API_ENDPOINT = 'https://api.openweathermap.org/data/2.5/forecast'
API_KEY=os.getenv("WEATHER_API_KEY")


def load_to_postgres(df, table_name):
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 5432))
    user = os.getenv("DB_USER", "airflow")
    password = os.getenv("DB_PASSWORD", "airflow")
    db_name = os.getenv("DB_NAME", "airflow_db")
    schema = 'weather_etl'

    print(f"Connecting to DB at {host}:{port} with user={user} dbname={db_name}")

    # Create schema and tables if not exists
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cur = conn.cursor()

        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema}.weather_current (
                id SERIAL PRIMARY KEY,
                city_id INT,
                city_name TEXT,
                timestamp TIMESTAMP,
                temp REAL,
                feels_like REAL,
                temp_min REAL,
                temp_max REAL,
                weather TEXT,
                description TEXT,
                temp_diff REAL,
                feeling TEXT,
                UNIQUE(city_id, timestamp)
            );
        """)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema}.weather_forecast (
                id SERIAL PRIMARY KEY,
                city_id INT,
                city_name TEXT,
                forecast_time TIMESTAMP,
                temp REAL,
                feels_like REAL,
                temp_min REAL,
                temp_max REAL,
                weather TEXT,
                description TEXT,
                temp_diff REAL,
                feeling TEXT,
                UNIQUE(city_id, forecast_time)
            );
        """)
        conn.commit()
        conn.close()
        print("Schema and tables created successfully!")
    except Exception as e:
        print("Failed during schema/table creation:", e)
        return

    # Insert data (if df is empty, skip)
    if df.empty:
        print("DataFrame is empty, skipping insert.")
        return

    try:
        engine = create_engine(
            f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}', 
            )
        with engine.begin() as connection:
            metadata = MetaData()
            metadata.reflect(bind=engine, schema=schema)
            full_table_name = f"{schema}.{table_name}"
            table = metadata.tables.get(full_table_name)
            if table is None:
                print(f"Table {full_table_name} does not exist.")
                return

            conflict_col = 'forecast_time' if table_name == 'weather_forecast' else 'timestamp'

            for _, row in df.iterrows():
                stmt = insert(table).values(**row.to_dict())
                stmt = stmt.on_conflict_do_nothing(index_elements=["city_id", conflict_col])
                connection.execute(stmt)
        print(f"Data successfully loaded into {schema}.{table_name}")
    except Exception as e:
        print("Failed to load data using ON CONFLICT:", e)


def list_city():
    """
    Return list cities in japan
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "city.list.json")
    with open (json_path, 'r') as file:
            data = json.load(file)

    japan_cities = [city for city in data if city.get("country") == "JP"]

    return japan_cities

def fetch_current_data(city_id, city_name):
    """
    Fetch data from the given URL and return it as a pandas DataFrame.
    
    Args:
        city_id and city_name: params to fetch data 
        
    Returns:
        pd.DataFrame: DataFrame containing the fetched data.
    """
    
        # current data 
    params = {
        'id': city_id,
        'appid': API_KEY,
        'units': 'metric',
    }
    response = requests.get(CURRENT_API_ENDPOINT, params=params)
    
    if response.status_code == 200:
        city_data = response.json()
        return pd.DataFrame([{
            'city_id': city_id,
            'city_name': city_name,
            'timestamp': datetime.utcnow().replace(minute=0, second=0, microsecond=0),
            'temp': city_data['main']['temp'],
            'feels_like': city_data['main']['feels_like'],
            'temp_min': city_data['main']['temp_min'],
            'temp_max': city_data['main']['temp_max'],
            'weather': city_data['weather'][0]['main'],
            'description': city_data['weather'][0]['description']
        }])
    else:
        print(f"Failed to fetch weather for (ID: {city_id})")


def fetch_forecast_data(city_id, city_name):
        """
    Fetch data from the given URL and return it as a pandas DataFrame.
    
    Args:
        city_id and city_name: params to fetch data 
        
    Returns:
        pd.DataFrame: DataFrame containing the fetched data.
    """
        #forecaste 12 hours with step = 3 and 4 blocks

        params_forecast = {
            'id': city_id,
            'appid': API_KEY,
            'units': 'metric',
            'cnt':4
        }
        res = requests.get(HOURLY_API_ENDPOINT, params=params_forecast)
        if res.status_code == 200:
            forcast_data = res.json()
            list_forcast = forcast_data.get("list")
            rows = []
            for hour in list_forcast:
                rows.append({
                'city_id': city_id,
                'city_name': city_name,
                'forecast_time': datetime.utcfromtimestamp(hour['dt']),
                'temp': hour['main']['temp'],
                'feels_like': hour['main']['feels_like'],
                'temp_min': hour['main']['temp_min'],
                'temp_max': hour['main']['temp_max'],
                'weather': hour['weather'][0]['main'],
                'description': hour['weather'][0]['description']
            })
            return pd.DataFrame(rows)

def categorize_temperature(feels_like, temp_min, temp_max):
    if feels_like > temp_max:
        return "Hot"
    
    elif feels_like < temp_min:
        return "Cold"
    
    else:
        return "Normal"
        
def transform_weather_data(df):

    #add different temperature 
    if 'temp_max' in df.columns and 'temp_min' in df.columns:
        df['temp_diff'] = df['temp_max'] - df['temp_min']
    
    df['feeling'] = df.apply(
        lambda row:categorize_temperature(row['feels_like'], row['temp_min'], row['temp_max']), 
        axis = 1
    )
    
    return df

def main():
    japan_cities = list_city()

    all_current_data = []
    all_forecast_data = []

    for city in japan_cities:
        city_id = city.get("id")
        city_name = city.get("name")
        print(f"Fetching data for {city_name}")

        df_current = transform_weather_data(fetch_current_data(city_id, city_name))
        df_forecast = transform_weather_data(fetch_forecast_data(city_id, city_name))

        print("Load to database")
        load_to_postgres(df_current,'weather_current')
        load_to_postgres(df_forecast, 'weather_forecast')
        print(f"Finish city {city_name}, please check ")


    #     print("Starting append")
    #     all_current_data.append(df_current)
    #     all_forecast_data.append(df_forecast)
    #     print("Finish append")

    # # Combine all city data into one DataFrame per table
    # print("Combine starting")
    # df_current_all = pd.concat(all_current_data, ignore_index=True)
    # df_forecast_all = pd.concat(all_forecast_data, ignore_index=True)
    # print("Combine ending")

    # # Load data in bulk
    # print("Loading to database ......")
    # load_to_postgres(df_current_all, 'weather_current')
    # load_to_postgres(df_forecast_all, 'weather_forecast')
    # print("All data is loaded. Please confirm")
    

if __name__ == "__main__":
    main()