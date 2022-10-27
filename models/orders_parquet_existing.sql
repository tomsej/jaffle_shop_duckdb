{{
    config(
        materialized='external',
        location='external/orders_existing.parquet'
    )
}}

select * from {{ ref('orders') }}