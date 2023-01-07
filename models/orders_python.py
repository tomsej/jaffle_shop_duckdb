#
def model(dbt, session):
    order_ref = dbt.ref("orders")
    return order_ref.df()
