import datetime
import re


def generate_order_number(pk):
    return f"ORDER-{datetime.datetime.now().strftime('%Y%m%d')}-{pk}"


def extract_points(point_string):
    match = re.search(r'\d+', point_string)
    if match:
        return int(match.group())
    return None
