{{
    config(
        materialized='external',
        location='external/orders_delim.csv',
        format='csv',
        delimiter='|'
    )
}}

select * from {{ ref('orders') }}