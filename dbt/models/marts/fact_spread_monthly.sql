with silver as (
    select * from {{ ref('stg_fred_observations') }}
),

monthly as (
    select
        series_id,
        date_trunc('month', observation_date)::date  as month,
        avg(spread_value)::numeric(6,2)              as avg_spread,
        min(spread_value)                            as min_spread,
        max(spread_value)                            as max_spread,
        count(*)                                     as observation_count
    from silver
    group by series_id, date_trunc('month', observation_date)
)

select * from monthly
order by series_id, month