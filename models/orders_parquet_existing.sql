{{ config(materialized="external") }} select * from {{ ref("orders") }}
