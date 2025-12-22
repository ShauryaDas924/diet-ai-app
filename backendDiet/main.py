# backend/main.py

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from logging_config import logger

# Internal modules
import nutrition as nut
import ai as diet_ai
import stores as store_mod


# -----------------------------
# App setup
# -----------------------------

app = FastAPI(
    title="Diet AI Backend",
    version="1.0.0",
    description="AI meal planning + nutrition + grocery + store discovery",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod: set to your frontend domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Pydantic request models
# -----------------------------

class UserProfile(BaseModel):
    # core personalization fields
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., description="male/female/other")
    height_cm: Optional[float] = None
    height_in: Optional[float] = None
    height_ft: Optional[float] = None
    weight_kg: Optional[float] = None
    weight_lb: Optional[float] = None

    activity_level: str = Field("moderate", description="sedentary/light/moderate/active/very_active")
    goal: str = Field("maintain", description="cut/maintain/bulk")

    # personalization / constraints
    dietary_preferences: Optional[Any] = None  # list or string (vegan, vegetarian, halal, etc.)
    allergies: Optional[Any] = None            # list or string
    budget: Optional[str] = None               # low/medium/high
    income: Optional[Any] = None               # optional numeric or string


class MealsPayload(BaseModel):
    meals: List[Dict[str, Any]]


class MealPlanRequest(BaseModel):
    user_profile: Dict[str, Any]


class WeeklyMealPlanRequest(BaseModel):
    user_profile: Dict[str, Any]


class MealSwapRequest(BaseModel):
    user_profile: Dict[str, Any]
    meal: str = Field("Dinner", description="Breakfast/Lunch/Dinner")
    constraint: Optional[str] = None


class MealRegenerateRequest(BaseModel):
    user_profile: Dict[str, Any]
    meal_type: str = Field("dinner", description="breakfast/lunch/dinner or Breakfast/Lunch/Dinner")
    constraint: Optional[str] = None


class MealCompareRequest(BaseModel):
    meal_a: Any
    meal_b: Any


class MealExplanationRequest(BaseModel):
    user_profile: Dict[str, Any]
    meal: Any


class GroceryListRequest(BaseModel):
    meals: List[Dict[str, Any]]


class DietComplianceRequest(BaseModel):
    user_profile: Dict[str, Any]
    meal: Dict[str, Any]


class PortionAdjustRequest(BaseModel):
    user_profile: Dict[str, Any]
    meal: Dict[str, Any]
    intensity: str = Field("normal", description="light/normal/strong")


class WhatIfRequest(BaseModel):
    user_profile: Dict[str, Any]
    meals: List[Dict[str, Any]]
    delta_calories: int = 0
    delta_protein_g: int = 0


class StoreScoreRequest(BaseModel):
    user_profile: Dict[str, Any]
    meals: List[Dict[str, Any]]
    store: Dict[str, Any]  # store object returned by /stores


class CheapestStoreRequest(BaseModel):
    user_profile: Dict[str, Any]
    meals: List[Dict[str, Any]]
    lat: float
    lng: float


class StoreMealMatchRequest(BaseModel):
    store: Dict[str, Any]
    meals: List[Dict[str, Any]]

# -----------------------------
# Rate limiting (simple IP-based)
# -----------------------------

import time
from fastapi import Request, Depends

_RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60      # seconds
RATE_LIMIT_MAX = 30         # requests per IP per window

def rate_limit(request: Request):
    ip = request.client.host
    now = time.time()

    window = _RATE_LIMIT.get(ip, [])
    window = [t for t in window if now - t < RATE_LIMIT_WINDOW]
    if not window:
        _RATE_LIMIT.pop(ip, None)
    if len(window) >= RATE_LIMIT_MAX:
        logger.warning(f"Rate limit exceeded for IP {ip}")
        raise HTTPException(status_code=429, detail="Too many requests")

    window.append(now)
    _RATE_LIMIT[ip] = window
# -----------------------------
# Meta / Health
# -----------------------------

@app.get("/")
def root():
    return {
        "message": "Diet AI API running",
        "docs": "/docs",
        "key_endpoints": [
            "/meal-plan",
            "/weekly-meal-plan",
            "/nutrition",
            "/calorie-target",
            "/macros",
            "/grocery-list",
            "/stores",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Profile / Targets
# -----------------------------

@app.post("/profile/validate")
def profile_validate(profile: UserProfile):
    # FastAPI/Pydantic already validates basics; we just return success.
    return {"valid": True}


@app.post("/calorie-target")
def calorie_target(profile: UserProfile):
    return nut.calorie_target(profile.dict(exclude_none=True))


@app.post("/macros")
def macros(profile: UserProfile):
    return nut.macro_targets(profile.dict(exclude_none=True))


# -----------------------------
# Meal planning (AI)
# -----------------------------

@app.post("/meal-plan", dependencies=[Depends(rate_limit)])
def meal_plan(req: MealPlanRequest):
    try:
        meals = diet_ai.generate_meal_plan(req.user_profile)
        nutrition = nut.calculate_nutrition(meals)
        score = nut.nutrition_score(meals, req.user_profile)

        return {
            "meals": meals,
            "nutrition": nutrition,
            "nutrition_score": score,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"meal-plan failed: {str(e)}")


@app.post("/weekly-meal-plan", dependencies=[Depends(rate_limit)])
def weekly_meal_plan(req: WeeklyMealPlanRequest):
    try:
        weekly = diet_ai.generate_weekly_meal_plan(req.user_profile)
        return {"week": weekly}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"weekly-meal-plan failed: {str(e)}")


@app.post("/meal-swap")
def meal_swap(req: MealSwapRequest):
    return diet_ai.swap_meal(req.dict())


@app.post("/meal-regenerate")
def meal_regenerate(req: MealRegenerateRequest):
    return diet_ai.meal_regenerate(req.dict())


@app.post("/meal-compare")
def meal_compare(req: MealCompareRequest):
    return diet_ai.compare_meals(req.dict())


@app.post("/meal-explanation")
def meal_explanation(req: MealExplanationRequest):
    return diet_ai.explain_meal_choice(req.dict())


# -----------------------------
# Nutrition utilities
# -----------------------------

@app.post("/nutrition")
def nutrition(req: MealsPayload):
    return nut.calculate_nutrition(req.meals)


@app.post("/nutrition-score")
def nutrition_score(profile: UserProfile, req: MealsPayload):
    return nut.nutrition_score(req.meals, profile.dict(exclude_none=True))


@app.post("/portion-adjust")
def portion_adjust(req: PortionAdjustRequest):
    return nut.portion_adjust(req.meal, req.user_profile, intensity=req.intensity)


@app.post("/what-if")
def what_if(req: WhatIfRequest):
    return nut.what_if(
        req.user_profile,
        req.meals,
        delta_calories=req.delta_calories,
        delta_protein_g=req.delta_protein_g,
    )


@app.post("/daily-summary")
def daily_summary(req: WhatIfRequest):
    # Re-using WhatIfRequest shape since it includes profile+meals
    return nut.daily_summary(req.user_profile, req.meals)


# -----------------------------
# Grocery
# -----------------------------

@app.post("/grocery-list")
def grocery_list(req: GroceryListRequest):
    return diet_ai.generate_grocery_list(req.meals)


# -----------------------------
# Diet compliance / safety checks
# -----------------------------

@app.post("/diet-compliance")
def diet_compliance(req: DietComplianceRequest):
    ok, reasons = diet_ai.diet_compliance_check(req.meal, req.user_profile)
    return {"ok": ok, "reasons": reasons}


# -----------------------------
# Stores / Maps (REAL Google Places via stores.py)
# -----------------------------

@app.get("/stores", dependencies=[Depends(rate_limit)])
def stores(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius_km: float = Query(5.0, description="Search radius in km"),
):
    try:
        # Returns live Google Places results enriched with your scoring fields
        return store_mod.find_stores(
            lat=lat,
            lng=lng,
            meals=None,
            user_profile=None,
            radius_km=radius_km,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"stores lookup failed: {str(e)}")


@app.post("/store-score")
def store_score(req: StoreScoreRequest):
    # store returned by /stores contains distance_km, price_level, etc.
    return store_mod.store_score(req.store, req.meals, req.user_profile)


@app.post("/cheapest-store")
def cheapest_store(req: CheapestStoreRequest):
    return store_mod.cheapest_store(req.meals, req.user_profile, req.lat, req.lng)


@app.post("/store-meal-match")
def store_meal_match(req: StoreMealMatchRequest):
    return store_mod.store_meal_match(req.store, req.meals)
