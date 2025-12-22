# backend/stores.py

from __future__ import annotations
from typing import Dict, List, Optional
import os
import requests
from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv
from cache import get as cache_get, set as cache_set
from logging_config import logger

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# -----------------------------
# Distance (Haversine)
# -----------------------------

def distance_km(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# -----------------------------
# Google Places Fetch
# -----------------------------

def fetch_nearby_stores(
    lat: float,
    lng: float,
    radius_m: int = 5000,
) -> List[Dict]:
    cache_key = f"places:{round(lat,4)}:{round(lng,4)}:{radius_m}"
    cached = cache_get(cache_key)
    if cached:
        logger.info("Google Places cache hit")
        return cached

    logger.info("Google Places cache miss")
    params = {
        "key": GOOGLE_API_KEY,
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "type": "grocery_or_supermarket",
    }

    resp = requests.get(PLACES_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    cache_set(cache_key, results, ttl_seconds=1800)  # 30 min cache
    return results

# -----------------------------
# Store Intelligence Layer
# -----------------------------

def find_stores(
    lat: float,
    lng: float,
    meals: Optional[List[Dict]] = None,
    user_profile: Optional[Dict] = None,
    radius_km: float = 5.0,
) -> List[Dict]:
    logger.info(f"find_stores called lat={lat}, lng={lng}, radius_km={radius_km}")
    """
    Main store discovery function.
    """
    raw_stores = fetch_nearby_stores(lat, lng, int(radius_km * 1000))
    results = []

    needed_ingredients = set()
    if meals:
        for m in meals:
            for ing in m.get("ingredients", []):
                needed_ingredients.add(ing.lower())

    budget = _normalize_budget(user_profile or {})

    for s in raw_stores:
        store_lat = s["geometry"]["location"]["lat"]
        store_lng = s["geometry"]["location"]["lng"]
        dist = distance_km(lat, lng, store_lat, store_lng)

        price_level = s.get("price_level", 2)  # 0–4 Google scale

        budget_match = (
            (budget == "low" and price_level <= 1) or
            (budget == "medium" and price_level <= 2) or
            (budget == "high")
        )

        # Ingredient coverage is estimated (Google doesn’t give inventory)
        coverage = estimate_ingredient_coverage(needed_ingredients, price_level)

        score = compute_store_score(
            distance_km=dist,
            coverage=coverage,
            price_level=price_level,
            budget_match=budget_match
        )

        results.append({
            "place_id": s["place_id"],
            "name": s["name"],
            "location": s["geometry"]["location"],
            "distance_km": round(dist, 2),
            "rating": s.get("rating"),
            "user_ratings_total": s.get("user_ratings_total"),
            "price_level": price_level,
            "open_now": s.get("opening_hours", {}).get("open_now"),
            "budget_match": budget_match,
            "ingredient_coverage_percent": coverage,
            "meal_plan_support_score": score,
            "why_recommended": explain_store_choice(dist, coverage, price_level),
        })

    return sorted(results, key=lambda x: x["meal_plan_support_score"], reverse=True)

# -----------------------------
# Your Unique Scoring Logic
# -----------------------------

def estimate_ingredient_coverage(ingredients: set, price_level: int) -> float:
    """
    Heuristic: higher-end stores usually have broader inventory.
    """
    if not ingredients:
        return 100.0

    base = {0: 0.6, 1: 0.7, 2: 0.8, 3: 0.9, 4: 0.95}.get(price_level, 0.75)
    return round(base * 100, 1)

def compute_store_score(
    distance_km: float,
    coverage: float,
    price_level: int,
    budget_match: bool,
) -> float:
    score = 0.0

    # Coverage (0–50)
    score += coverage * 0.5

    # Distance (0–25)
    score += max(0, 25 - distance_km * 3)

    # Budget alignment (0–15)
    if budget_match:
        score += 15

    # Price sanity (0–10)
    score += max(0, 10 - abs(price_level - 2) * 3)

    return round(min(score, 100.0), 1)

def explain_store_choice(distance_km, coverage, price_level):
    reasons = []
    if coverage > 80:
        reasons.append("Supports most ingredients in your meal plan")
    if distance_km < 3:
        reasons.append("Very close to you")
    if price_level <= 2:
        reasons.append("Budget-friendly pricing")
    return "; ".join(reasons)

def _normalize_budget(profile: Dict) -> str:
    income = profile.get("income")
    if isinstance(income, (int, float)):
        if income < 25000:
            return "low"
        if income > 80000:
            return "high"
    return "medium"
