{{
    config(
        materialized='incremental',
        unique_key='id',
        on_schema_change='append_new_columns'
    )
}}


select
    id,
    fruit,
    cost_per_pound_dollars as cost,
    quantity,
    cost_per_pound_dollars * quantity as total_cost,
    country_of_origin
from {{ref('fruits_update')}}