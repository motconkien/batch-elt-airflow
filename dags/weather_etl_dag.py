# dags/weather_etl_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def run_etl():
    subprocess.run(["python3", "/opt/airflow/etl/etl.py"], check=True)

with DAG(
    "weather_etl_pipeline",
    default_args=default_args,
    description="Run ETL script for weather data",
    schedule_interval="@hourly",  
    start_date=datetime(2025, 6, 15),
    catchup=False,
    tags=["weather", "ETL"],
) as dag:

    etl_task = PythonOperator(
        task_id="run_weather_etl_script",
        python_callable=run_etl,
    )

    etl_task
