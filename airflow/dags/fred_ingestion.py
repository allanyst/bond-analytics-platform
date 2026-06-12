from __future__ import annotations
import sys
sys.path.insert(0, '/opt/airflow/src')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from ingestion.fred_client import fetch_series
from ingestion.loaders import load_to_bronze

SERIES_ID = "BAMLH0A0HYM2"

def extract(**context):
    observations = fetch_series(SERIES_ID)
    context["ti"].xcom_push(key="observations", value=observations)

def load(**context):
    observations = context["ti"].xcom_pull(
        task_ids="extract",    # ← task_id del extract
        key="observations"
    )
    load_to_bronze(SERIES_ID, observations)

with DAG(
    dag_id="fred_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 0 * * *",
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
    )

    extract_task >> load_task