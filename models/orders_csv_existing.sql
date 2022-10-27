{{
    config(
        materialized='external',
        location='external/orders_existing.csv',
        format='csv'
    )
}}

select * from {{ ref('orders') }}