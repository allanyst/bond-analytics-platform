from __future__ import annotations
import os
import psycopg2
from datetime import datetime

def load_to_bronze(series_id: str, observations: list) -> None:
    conn = psycopg2.connect(
        host="postgres",
        dbname=os.environ.get("BONDS_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )
    
    cursor = conn.cursor()
    
    for obs in observations:
        if obs["value"] == ".":  
            continue
            
        cursor.execute("""
            INSERT INTO bronze.fred_observations
                (series_id, observation_date, value, realtime_start, realtime_end)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT fred_observations_unique DO NOTHING
        """, (
            series_id,              # series_id
            obs["date"],       # fecha de observación
            obs["value"],       # valor
            obs["realtime_start"],       # realtime_start
            obs["realtime_end"],       # realtime_end
        ))
    
    conn.commit()
    cursor.close()
    conn.close()