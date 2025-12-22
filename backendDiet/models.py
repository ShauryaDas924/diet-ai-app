# backend/models.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ======================================================
# USER / PROFILE MODELS
# ======================================================

class UserProfile(BaseModel):
    """
    Core personalization model.
    Used by:
      - nutrition.py
      - ai.py
      - stores.py (budget logic)
    """

    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., description="male / female / other")

    # Height (accepts multiple units)
    height_cm: Optional[float] = None
    height_in: Optional[float] = None
    height_ft: Optional[float] = None

    # Weight (accepts multiple units)
    weight_kg: Optional[float] = None
    weight_lb: Optional[float] = None

    activity_level: str = Field(
        "moderate",
        description="sedentary | light | moderate | active | very_active",
    )

    goal: str = Field(
        "maintain",
        description="cut | maintain | bulk",
    )

    # Constraints / preferences
    dietary_preferences: Optional[Any] = None  # list or string
    allergies: Optional[Any] = None            # list or string

    # Financial
    budget: Optional[str] = Field(
        None,
        description="low | medium | high",
    )
    income: Optional[Any] = None


# ======================================================
# MEAL / NUTRITION MODELS
# ======================================================

class Meal(BaseModel):
    """
    Canonical meal schema.
    Returned by ai.py and consumed by nutrition.py & stores.py.
    """

    meal: Optional[str] = Field(
        None,
        description="Breakfast / Lunch / Dinner (label)",
    )

    name: str

    calories: int
    protein: int
    carbs: int
    fat: int

    fiber: Optional[int] = 0
    sugar: Optional[int] = 0
    sodium_mg: Optional[int] = 0

    cost_estimate: Optional[float] = None

    ingredients: List[str] = Field(default_factory=list)
    allergens: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)


class NutritionSummary(BaseModel):
    """
    Aggregate nutrition output for a set of meals.
    """

    calories: int
    protein: int
    carbs: int
    fat: int

    fiber: Optional[int] = 0
    sugar: Optional[int] = 0
    sodium_mg: Optional[int] = 0

    macro_percentages: Optional[Dict[str, float]] = None


class NutritionScore(BaseModel):
    """
    Quality scoring output.
    """

    score: float = Field(..., ge=0, le=100)
    reasons: List[str]


# ======================================================
# MEAL PLAN MODELS
# ======================================================

class DailyMealPlan(BaseModel):
    """
    One-day meal plan.
    """

    meals: List[Meal]
    nutrition: Optional[NutritionSummary] = None
    nutrition_score: Optional[NutritionScore] = None


class WeeklyMealPlan(BaseModel):
    """
    7-day meal plan.
    """

    day: int = Field(..., ge=1, le=7)
    meals: List[Meal]


# ======================================================
# GROCERY MODELS
# ======================================================

class GroceryList(BaseModel):
    """
    Grocery list derived from meals.
    """

    items: List[str]
    missing: Optional[List[str]] = Field(default_factory=list)
    count: int


# ======================================================
# STORE / MAP MODELS
# ======================================================

class Store(BaseModel):
    """
    Enriched store object (Google Places + your intelligence).
    """

    place_id: str
    name: str

    location: Dict[str, float]  # {lat, lng}

    distance_km: float

    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[int] = None

    open_now: Optional[bool] = None

    # Your app’s unique intelligence
    budget_match: Optional[bool] = None
    ingredient_coverage_percent: Optional[float] = None
    meal_plan_support_score: Optional[float] = None
    why_recommended: Optional[str] = None


class StoreScore(BaseModel):
    """
    Store scoring output.
    """

    store_id: str
    store_name: str
    score: float
    reasons: List[str]


class StoreMealMatch(BaseModel):
    """
    Store vs meal plan compatibility.
    """

    store_id: str
    store_name: str

    covered_items: List[str]
    missing_items: List[str]

    coverage_percent: float


# ======================================================
# REQUEST PAYLOAD MODELS (OPTIONAL SHARED)
# ======================================================

class MealRegenerateRequest(BaseModel):
    user_profile: UserProfile
    meal_type: str
    constraint: Optional[str] = None


class MealSwapRequest(BaseModel):
    user_profile: UserProfile
    meal: str
    constraint: Optional[str] = None
