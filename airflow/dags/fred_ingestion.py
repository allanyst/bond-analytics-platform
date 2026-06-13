from __future__ import annotations
import sys
import os
import psycopg2
sys.path.insert(0, '/opt/airflow/src')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
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

def check_fallen_angels(**context):
    conn = psycopg2.connect(
        host="postgres",
        dbname=os.environ.get("BONDS_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT actual.bond_id, actual.agency, prev.rating, actual.rating
        FROM snapshots.rating_history_snapshot actual
        JOIN snapshots.rating_history_snapshot prev
            ON actual.bond_id = prev.bond_id
            AND actual.agency = prev.agency
            AND prev.dbt_valid_to IS NOT NULL
        WHERE actual.dbt_valid_to IS NULL
          AND actual.rating = 'BB'
          AND prev.rating = 'BBB'
    """)
    fallen_angels = cursor.fetchall()
    cursor.close()
    conn.close()

    if fallen_angels:
        msg = f"FALLEN ANGELS DETECTED: {len(fallen_angels)} bonds downgraded BBB→BB"
        for fa in fallen_angels:
            msg += f"\n  bond_id={fa[0]} agency={fa[1]}"
        raise ValueError(msg)
    
    print("No fallen angels detected.")

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

    dbt_run_task = BashOperator(
        task_id="dbt_run",
        bash_command="docker exec bond-analytics-platform-dbt-1 dbt run --profiles-dir /opt/dbt",
    )

    dbt_test_task = BashOperator(
        task_id="dbt_test",
        bash_command="docker exec bond-analytics-platform-dbt-1 dbt test --profiles-dir /opt/dbt",
    )

    check_task = PythonOperator(
        task_id="check_fallen_angels",
        python_callable=check_fallen_angels,
    )

    extract_task >> load_task >> dbt_run_task >> dbt_test_task >> check_task