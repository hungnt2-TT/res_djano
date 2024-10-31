from haversine import haversine, Unit

from marketplace.constants import COST_PER_KILOMETER, COST_PER_MINUTE, AVE_SPEED_KMH


def calculate_distance(coord1, coord2):
    return haversine(coord1, coord2, unit=Unit.KILOMETERS)


def estimate_time(distance_km):
    return distance_km / AVE_SPEED_KMH * 60


def calculate_shipping_cost(distance_km, time_minutes):
    cost_distance = distance_km * COST_PER_KILOMETER
    cost_time = time_minutes * COST_PER_MINUTE
    return cost_distance + cost_time
