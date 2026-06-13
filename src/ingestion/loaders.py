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

def load_bonds_to_bronze(bonds: list, ratings: list) -> None:
    conn = psycopg2.connect(
        host="postgres",
        dbname=os.environ.get("BONDS_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )
    cursor = conn.cursor()

    for bond in bonds:
        cursor.execute("""
            INSERT INTO bronze.bonds
                (bond_id, isin, issuer, sector, issue_date, maturity_date, coupon_rate, face_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (bond_id) DO NOTHING
        """, (
            bond['bond_id'], bond['isin'], bond['issuer'], bond['sector'],
            bond['issue_date'], bond['maturity_date'], bond['coupon_rate'], bond['face_value']
        ))

    for rating in ratings:
        cursor.execute("""
            INSERT INTO bronze.rating_history
                (bond_id, agency, rating, effective_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT rating_history_unique DO NOTHING
        """, (
            rating['bond_id'], rating['agency'], rating['rating'], rating['effective_date']
        ))

    conn.commit()
    cursor.close()
    conn.close()