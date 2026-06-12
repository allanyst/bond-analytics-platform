\c bonds_db;
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE TABLE IF NOT EXISTS bronze.fred_observations (
    id              SERIAL PRIMARY KEY,
    series_id       VARCHAR(20)  NOT NULL,
    observation_date DATE        NOT NULL,
    value           VARCHAR(10)  NOT NULL,
    realtime_start  DATE,
    realtime_end    DATE,
    ingested_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fred_observations_unique UNIQUE (series_id, observation_date)
);