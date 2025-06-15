# 💾 Batch ETL Pipeline with Airflow (Crypto API Example)

## 🌟 Overview

This project demonstrates a **batch ETL pipeline** using **Apache Airflow** to extract, transform, and load data from a public API into a database. The data is fetched periodically and made available for analysis and visualization.

Key Features:
- Extracts data from a public **Weather API**
- Transforms and cleans data using **Pandas**
- Loads data into **PostgreSQL** (or SQLite)
- Uses **Airflow DAGs** to schedule and orchestrate ETL jobs
- Adds logging, error handling, and optional unit testing
- Uses **Streamlit dashboard** to display results

---

## 🛠 Tech Stack

| Component    | Tool/Service           |
|--------------|-------------------------|
| Orchestration| Apache Airflow          |
| Source       | Open Weather            |
| Processing   | Python + Pandas         |
| Database     | PostgreSQL or SQLite    |
| Container    | Docker, Docker Compose  |
| Visualization| Streamlit (optional)    |

---

## 🧱 Project Structure
```
batch-etl-airflow/
├── scripts/
│   └── elt.py
├── weather_etl_dag.py

dashboard/
├── main.py
├── Procfile

etl/
├── city.list.json
├── etl.py

logs/

docker-compose.yml
Dockerfile
requirements.txt
```