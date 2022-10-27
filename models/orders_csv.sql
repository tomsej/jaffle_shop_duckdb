{{
    config(
        materialized='external',
        location='external/orders.csv',
        format='csv'
    )
}}

select * from {{ ref('orders') }}