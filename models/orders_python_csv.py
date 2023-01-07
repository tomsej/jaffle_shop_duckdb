#
def model(dbt, session):
    dbt.config(
        materialized="external",
        format="csv",
        delimiter="|",
    )
    order_ref = dbt.ref("orders")
    return order_ref.df()
