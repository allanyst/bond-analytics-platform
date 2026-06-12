from __future__ import annotations
import os
import requests
from datetime import datetime

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

def fetch_series(series_id: str) -> list[dict]:
    api_key = os.environ.get("FRED_API_KEY")
    
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()  # lanza un error si la respuesta no es 200
    
    data = response.json()
    return data["observations"]  # devuelve la lista de observaciones