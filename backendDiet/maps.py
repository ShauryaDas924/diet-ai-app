# backend/maps.py
from __future__ import annotations

from math import radians, sin, cos, sqrt, atan2
from typing import Tuple


# -----------------------------
# Constants
# -----------------------------

EARTH_RADIUS_KM = 6371.0


# -----------------------------
# Distance (Haversine)
# -----------------------------

def distance_km(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
) -> float:
    """
    Calculate great-circle distance between two coordinates (km).
    Deterministic, fast, and accurate for app-scale usage.
    """
    lat1_r, lng1_r = radians(lat1), radians(lng1)
    lat2_r, lng2_r = radians(lat2), radians(lng2)

    dlat = lat2_r - lat1_r
    dlng = lng2_r - lng1_r

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1_r) * cos(lat2_r) * sin(dlng / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c


# -----------------------------
# Radius check
# -----------------------------

def within_radius(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
    radius_km: float,
) -> bool:
    """
    Returns True if (lat2, lng2) is within radius_km of (lat1, lng1).
    """
    return distance_km(lat1, lng1, lat2, lng2) <= radius_km


# -----------------------------
# Bounding box (performance helper)
# -----------------------------

def bounding_box(
    lat: float,
    lng: float,
    radius_km: float,
) -> Tuple[float, float, float, float]:
    """
    Approximate bounding box for a radius (used to pre-filter places).
    Returns: (min_lat, max_lat, min_lng, max_lng)
    """
    lat_delta = radius_km / 111.0  # ~111 km per degree latitude
    lng_delta = radius_km / (111.0 * cos(radians(lat)))

    return (
        lat - lat_delta,
        lat + lat_delta,
        lng - lng_delta,
        lng + lng_delta,
    )


# -----------------------------
# Utility: midpoint (optional)
# -----------------------------

def midpoint(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
) -> Tuple[float, float]:
    """
    Returns midpoint between two coordinates.
    Useful for map centering.
    """
    lat1_r, lng1_r = radians(lat1), radians(lng1)
    lat2_r, lng2_r = radians(lat2), radians(lng2)

    bx = cos(lat2_r) * cos(lng2_r - lng1_r)
    by = cos(lat2_r) * sin(lng2_r - lng1_r)

    lat3 = atan2(
        sin(lat1_r) + sin(lat2_r),
        sqrt((cos(lat1_r) + bx) ** 2 + by ** 2),
    )
    lng3 = lng1_r + atan2(by, cos(lat1_r) + bx)

    return (lat3 * 180 / 3.141592653589793, lng3 * 180 / 3.141592653589793)
