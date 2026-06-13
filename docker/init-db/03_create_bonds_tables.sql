\c bonds_db;

CREATE TABLE IF NOT EXISTS bronze.bonds (
    bond_id      INTEGER PRIMARY KEY,
    isin         VARCHAR(12) NOT NULL,
    issuer       VARCHAR(50) NOT NULL,
    sector       VARCHAR(30) NOT NULL,
    issue_date   DATE NOT NULL,
    maturity_date DATE NOT NULL,
    coupon_rate  NUMERIC(5,2) NOT NULL,
    face_value   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bronze.rating_history (
    id             SERIAL PRIMARY KEY,
    bond_id        INTEGER NOT NULL REFERENCES bronze.bonds(bond_id),
    agency         VARCHAR(10) NOT NULL,
    rating         VARCHAR(5) NOT NULL,
    effective_date DATE NOT NULL,
    ingested_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT rating_history_unique UNIQUE (bond_id, agency, effective_date)
);