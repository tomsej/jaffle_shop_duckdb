#
def model(dbt, session):
  dbt.config(materialized="external", location="external/python_existing.parquet")
  order_ref = dbt.ref("orders")
  return order_ref.df()