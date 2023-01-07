#
def model(dbt, session):
    dbt.config(materialized="external")
    order_ref = dbt.ref("orders")
    return order_ref.df()
