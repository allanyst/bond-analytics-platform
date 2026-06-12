
  create view "bonds_db"."silver"."stg_fred_observations__dbt_tmp"
    
    
  as (
    with source as (
    select * from "bonds_db"."bronze"."fred_observations"
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
  );