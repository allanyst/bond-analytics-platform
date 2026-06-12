with source as (
    select * from {{ source('bronze', 'fred_observations') }}
),

renamed as (
    select
        id,
        series_id,
        observation_date,
        value::numeric       as spread_value,
        realtime_start,
        realtime_end,
        ingested_at
    from source
)

select * from renamed