{% snapshot rating_history_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='id',
        strategy='check',
        check_cols=['rating'],
    )
}}

select
    id,
    bond_id,
    agency,
    rating,
    effective_date
from {{ source('bronze', 'rating_history') }}

{% endsnapshot %}