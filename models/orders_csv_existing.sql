{{ config(materialized="external", format="csv") }} select * from {{ ref("orders") }}
