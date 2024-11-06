from haversine import haversine, Unit

from marketplace.constants import COST_PER_KILOMETER, COST_PER_MINUTE, AVE_SPEED_KMH, FIRST_KM_COST, LAST_KM_COST


def calculate_distance(coord1, coord2):
    return haversine(coord1, coord2, unit=Unit.KILOMETERS)


def estimate_time(distance_km):
    return distance_km / AVE_SPEED_KMH * 60


def calculate_shipping_cost(distance_km):
    cost_distance = cost_distance_km(distance_km)
    return cost_distance


def cost_distance_km(distance_km):
    if isinstance(distance_km, str):
        distance_km = float(distance_km.split()[0])

    if distance_km <= 3.0:
        return FIRST_KM_COST
    else:
        # Tính phí cho 3 km đầu tiên
        total_cost = FIRST_KM_COST
        # Tính phí cho các km vượt quá
        excess_distance = distance_km - 3.0
        total_cost += excess_distance * LAST_KM_COST
        return total_cost
