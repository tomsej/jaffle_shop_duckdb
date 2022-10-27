{{
    config(
        materialized='external',
        location='external/orders.parquet'
    )
}}

select * from {{ ref('orders') }}