{{
    config(
        materialized="external",
        format="csv",
        delimiter="|",
    )
}} select * from {{ ref("orders") }}
