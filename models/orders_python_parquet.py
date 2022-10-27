#
def model(dbt, session):
  dbt.config(materialized="external", location="external/python.parquet")
  order_ref = dbt.ref("orders")
  return order_ref.df()