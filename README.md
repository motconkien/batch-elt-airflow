# 💾 Batch ETL Pipeline with Airflow 

## 🌟 Overview

This project demonstrates a **batch ETL pipeline** using **Apache Airflow** to extract, transform, and load data from a public API into a database. The data is fetched periodically and made available for analysis and visualization.

Key Features:
- Extracts data from a public **Weather API**
- Transforms and cleans data using **Pandas**
- Loads data into **PostgreSQL** 
- Uses **Airflow DAGs** to schedule and orchestrate ETL jobs
- Uses **Streamlit dashboard** to display results

---

## 🛠 Tech Stack

| Component    | Tool/Service           |
|--------------|-------------------------|
| Orchestration| Apache Airflow          |
| Source       | Open Weather            |
| Processing   | Python + Pandas         |
| Database     | PostgreSQL              |
| Container    | Docker, Docker Compose  |
| Visualization| Streamlit               |

---

## 🧱 Project Structure
```
├── dashboard/
│   ├── main.py      
│   └── Procfile                 
│
├── output/
│   ├── current.csv
│   └── forecast.csv
│
├── dags/
│   └── weather_etl_dag.py       
│
├── etl/
│   └── etl.py 
|   └── city.list.json            
│
├── .env                        
├── .gitignore                  # Git ignore file
├── Dockerfile
├── README.md                   # This README file
├── requirements.txt            # Python dependencies

```

## 📋 Usage
- Retrieving weather data from OpenWeather API and storing it in PostgreSQL.
- Airflow orchestrates the ETL pipeline to fetch and process data regularly.
- Streamlit dashboard reads from PostgreSQL to visualize current and forecast weather data interactively.
