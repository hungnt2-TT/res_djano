import datetime


def generate_order_number(pk):
    return f"ORDER-{datetime.datetime.now().strftime('%Y%m%d')}-{pk}"
