import streamlit as st
import pandas as pd 
import psycopg2
import time

@st.cache_data(ttl=300)
def load_data(): 
    conn = psycopg2.connect(
        host='localhost',
        database='airflow_db',
        user='airflow',
        password='airflow',
        port=5432
    )

    query = "SELECT*FROM weather_etl.weather_current"
    df = pd.read_sql(query,conn)

    query_forecast = "SELECT*FROM weather_etl.weather_forecast"
    df_forecast = pd.read_sql(query_forecast,conn)
    conn.close()
    return df, df_forecast

def current_data():
    st.title("🌤️ Weather Dashboard - Current Data")
    df_current, df_forecast = load_data()

    #slide bar
    cities = ["All Cities"] + sorted(df_current['city_name'].unique()) 
    city_selected = st.selectbox('Select City', cities)

    if city_selected != "All Cities":
        df_filtered = df_current[df_current['city_name'] == city_selected]
    else: 
        df_filtered = df_current

    st.subheader(f"Recent data for {city_selected}")
    st.dataframe(df_filtered)

    if not df_filtered.empty and city_selected != "All Cities":
        latest = df_filtered.iloc[0]
        col1, col2, col3, col4,col5 = st.columns(5)
        col1.metric("Current Temperature (°C)", latest['temp'])
        col2.metric("Min Temperature (°C)", latest['temp_min'])
        col3.metric("Max Temperature (°C)", latest['temp_max'])
        col4.metric("Diff Temperature (°C)", latest['temp_diff'])
        col5.metric("Feels like (°C)", latest['feels_like'])

  
        st.markdown(f"### Weather:  {latest['weather']}")
        

        st.markdown(f"### Description: {latest['description']}")
        st.markdown(f"### Status: {latest['feeling']}")


def forecast_data():
    st.title("🌤️ Weather Dashboard - Forecast Data")
    df_current, df_forecast = load_data()

    cities = ['All cities'] + sorted(df_forecast["city_name"].unique())
    city_selected = st.selectbox('Select City', cities)

    # Fix capitalization mismatch
    if city_selected != "All cities":
        df_filtered = df_forecast[df_forecast['city_name'] == city_selected]
    else: 
        df_filtered = df_forecast

    # Check for empty dataframe
    if df_filtered.empty:
        st.warning(f"No forecast data available for {city_selected}")
    else:
        st.subheader(f"Forecast data for {city_selected}")
        st.dataframe(df_filtered[['forecast_time', 'temp', 'temp_min', 'temp_max', 'weather', 'description', 'feels_like', 'feeling']])


pages = {
    "Menu": [
        st.Page(current_data, title="Current weather", icon="📊"),
        st.Page(forecast_data, title='Forecast weather', icon="🔥")
    ]
}

pg = st.navigation(pages)
pg.run()


    