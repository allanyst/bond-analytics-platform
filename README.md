# Bond Analytics Platform

End-to-end Data Engineering pipeline for fixed income analytics, built with Apache Airflow, dbt, PostgreSQL, and Docker. Ingests real market spread data from the Federal Reserve (FRED API) and processes it through a medallion architecture to produce analytics-ready datasets.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION                            │
│                      Apache Airflow 2.8                         │
│                                                                 │
│  extract ──► load ──► dbt_run ──► dbt_test ──► check_fallen    │
└────┬──────────────────────┬──────────────────────────┬──────────┘
     │                      │                          │
     ▼                      ▼                          ▼
┌─────────┐         ┌──────────────┐         ┌────────────────┐
│  FRED   │         │    BRONZE    │         │  FALLEN ANGEL  │
│   API   │──────►  │  Raw tables  │         │   DETECTION    │
│ (FRED)  │         │  PostgreSQL  │         │  BBB → BB SCD  │
└─────────┘         └──────┬───────┘         └────────────────┘
                           │
                    dbt transform
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌────────────┐           ┌──────────────┐
       │   SILVER   │           │   SNAPSHOTS  │
       │  dbt views │           │  SCD Type 2  │
       │  (staging) │           │  rating hist │
       └─────┬──────┘           └──────────────┘
             │
      dbt aggregate
             │
             ▼
       ┌────────────┐
       │    GOLD    │
       │ dbt tables │
       │  (marts)   │
       └─────┬──────┘
             │
             ▼
    ┌─────────────────┐
    │    NOTEBOOK     │
    │ Spread analysis │
    │ Rating distrib. │
    │ Crisis periods  │
    └─────────────────┘
```

## Stack

| Layer         | Technology              |
|---------------|-------------------------|
| Orchestration | Apache Airflow 2.8      |
| Transform     | dbt 1.8 (postgres)      |
| Storage       | PostgreSQL 15           |
| Ingestion     | Python + FRED API       |
| Containers    | Docker / Docker Compose |
| Testing       | pytest                  |
| Analysis      | Jupyter + pandas + matplotlib |

## Data Flow

### Bronze — Raw Ingestion
- **`bronze.fred_observations`** — Daily HY spread observations from FRED (series `BAMLH0A0HYM2`)
- **`bronze.bonds`** — Synthetic bond master data (500 bonds across sectors)
- **`bronze.rating_history`** — Credit rating events per bond and agency

All inserts are idempotent via `ON CONFLICT DO NOTHING`.

### Silver — Standardized Views (dbt)
- **`silver.stg_fred_observations`** — Casts spread value to numeric, filters nulls
- **`silver.stg_rating_history`** — Clean view over raw rating events

### Gold — Analytics-Ready (dbt)
- **`gold.fact_spread_monthly`** — Monthly aggregation: avg, min, max spread and observation count

### Snapshots — SCD Type 2
- **`snapshots.rating_history_snapshot`** — Tracks rating changes over time with `dbt_valid_from` / `dbt_valid_to`, enabling point-in-time analysis

## Key Features

**Fallen Angel Detection**
The pipeline automatically detects bonds downgraded from BBB to BB (investment grade → high yield) by querying the SCD Type 2 snapshot. The Airflow task raises an alert if any fallen angels are found.

**Idempotent Pipeline**
All Bronze ingestion uses `ON CONFLICT DO NOTHING` — re-running the DAG never produces duplicates.

**dbt Isolation**
dbt runs in a separate Python 3.11 container (Airflow uses Python 3.8, which is incompatible with dbt 1.8). Airflow triggers dbt via `docker exec` using a mounted Docker socket.

## Project Structure

```
bond-analytics-platform/
├── airflow/
│   └── dags/
│       └── fred_ingestion.py      # Main DAG
├── dbt/
│   ├── models/
│   │   ├── staging/               # Silver layer
│   │   └── marts/                 # Gold layer
│   ├── snapshots/                 # SCD Type 2
│   └── macros/                    # Schema routing
├── docker/
│   └── init-db/                   # PostgreSQL init scripts
├── notebooks/
│   └── bond_analysis.ipynb        # Spread & rating analysis
├── src/
│   └── ingestion/
│       ├── fred_client.py         # FRED API client
│       ├── loaders.py             # Bronze loaders
│       └── synthetic_bonds.py     # Synthetic data generator
├── tests/
│   ├── test_fred_client.py        # Unit tests
│   └── test_loaders.py
└── docker-compose.yml
```

## Setup

### Prerequisites
- Docker + Docker Compose
- FRED API key (free at https://fred.stlouisfed.org/docs/api/api_key.html)

### Environment variables
Create a `.env` file:
```
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=postgres
BONDS_DB=bonds_db
FRED_API_KEY=your_key_here
```

### Run
```bash
# Start all services
docker compose up -d

# Fix log permissions (first time only)
sudo chown -R 50000:0 airflow/logs

# Access Airflow UI
open http://localhost:8081  # admin / admin
```

### Tests
```bash
pip install pytest requests psycopg2-binary
pytest tests/ -v
```

## Analysis

Open the notebook after the pipeline has run:
```bash
jupyter notebook notebooks/bond_analysis.ipynb
```

Charts included:
- HY Spread monthly trend with min/max range
- Annual spread volatility (identifies 2008, 2020, 2022 crisis periods)
- Bond rating distribution across the synthetic portfolio
- Fallen angel detection output
- Spread behavior during GFC, COVID-19, and 2022 rate hike cycle
