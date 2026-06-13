{{ config(materialized='view') }}

SELECT
    id,
    bond_id,
    agency,
    rating,
    effective_date,
    ingested_at
FROM {{ source('bronze', 'rating_history') }}
