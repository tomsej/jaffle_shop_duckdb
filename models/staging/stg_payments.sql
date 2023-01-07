with
    {#-
    Normally we would select from the table here, but we are using seeds to load
    our data in this project
    #}
    source as (select * from {{ ref("raw_payments") }}),
    renamed as (
        -- `amount` is currently stored in cents, so we convert it to dollars
        select id as payment_id, order_id, payment_method, amount / 100 as amount
        from source
    )
select *
from renamed
