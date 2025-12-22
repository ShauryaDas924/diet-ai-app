# backend/nutrition.py
"""
Deterministic nutrition engine.

Responsibilities:
- Calorie targets (BMR / TDEE / goals)
- Macro targets
- Nutrition aggregation
- Nutrition scoring (explainable)
- Portion adjustment
- What-if simulations
- Daily summaries

NO AI
NO DATABASE
PURE LOGIC
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
import math


# ======================================================
# CONSTANTS
# ======================================================

KCAL_PER_GRAM = {
    "protein": 4,
    "carbs": 4,
    "fat": 9,
}

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


# ======================================================
# HELPERS
# ======================================================

def _lower(x: Any) -> str:
    return str(x).strip().lower() if x is not None else ""

def _to_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# ======================================================
# PROFILE NORMALIZATION
# ======================================================

def _gender(profile: Dict) -> str:
    g = _lower(profile.get("gender"))
    if g in {"male", "m"}:
        return "male"
    if g in {"female", "f"}:
        return "female"
    return "other"

def _height_cm(profile: Dict) -> float:
    if profile.get("height_cm"):
        return _to_float(profile["height_cm"])
    if profile.get("height_ft") or profile.get("height_in"):
        ft = _to_float(profile.get("height_ft"))
        inch = _to_float(profile.get("height_in"))
        return (ft * 12 + inch) * 2.54
    if profile.get("height_in"):
        return _to_float(profile["height_in"]) * 2.54
    return 0.0

def _weight_kg(profile: Dict) -> float:
    if profile.get("weight_kg"):
        return _to_float(profile["weight_kg"])
    if profile.get("weight_lb"):
        return _to_float(profile["weight_lb"]) * 0.453592
    return 0.0

def _age(profile: Dict) -> float:
    return _to_float(profile.get("age"))

def _activity(profile: Dict) -> float:
    return ACTIVITY_MULTIPLIERS.get(
        _lower(profile.get("activity_level", "moderate")),
        ACTIVITY_MULTIPLIERS["moderate"],
    )

def _goal(profile: Dict) -> str:
    g = _lower(profile.get("goal"))
    if g in {"cut", "lose", "deficit"}:
        return "cut"
    if g in {"bulk", "gain", "surplus"}:
        return "bulk"
    return "maintain"


# ======================================================
# CORE CALCULATIONS
# ======================================================

def calculate_bmr(profile: Dict) -> float:
    """
    Mifflin-St Jeor Equation
    """
    weight = _weight_kg(profile)
    height = _height_cm(profile)
    age = _age(profile)
    gender = _gender(profile)

    base = 10 * weight + 6.25 * height - 5 * age
    if gender == "male":
        return base + 5
    if gender == "female":
        return base - 161
    return base - 78  # neutral average


def calculate_tdee(profile: Dict) -> float:
    return calculate_bmr(profile) * _activity(profile)


def calorie_target(profile: Dict) -> Dict:
    tdee = calculate_tdee(profile)
    goal = _goal(profile)

    factor = 1.0
    if goal == "cut":
        factor = 0.85
    elif goal == "bulk":
        factor = 1.1

    target = int(round(tdee * factor))

    return {
        "goal": goal,
        "bmr": int(round(calculate_bmr(profile))),
        "tdee": int(round(tdee)),
        "calorie_target": target,
    }


def macro_targets(profile: Dict) -> Dict:
    cal = calorie_target(profile)["calorie_target"]
    weight = _weight_kg(profile)
    goal = _goal(profile)

    protein_per_kg = 1.8 if goal == "bulk" else 1.6
    protein_g = int(round(weight * protein_per_kg))
    protein_kcal = protein_g * 4

    fat_kcal = cal * 0.25
    fat_g = int(round(fat_kcal / 9))

    carbs_kcal = max(0, cal - protein_kcal - fat_kcal)
    carbs_g = int(round(carbs_kcal / 4))

    return {
        "calories": cal,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
    }


# ======================================================
# MEAL AGGREGATION
# ======================================================

def calculate_nutrition(meals: List[Dict]) -> Dict:
    totals = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "fiber": 0,
        "sugar": 0,
        "sodium_mg": 0,
        "cost_estimate": 0.0,
    }

    for meal in meals:
        totals["calories"] += int(meal.get("calories", 0))
        totals["protein"] += int(meal.get("protein", 0))
        totals["carbs"] += int(meal.get("carbs", 0))
        totals["fat"] += int(meal.get("fat", 0))
        totals["fiber"] += int(meal.get("fiber", 0))
        totals["sugar"] += int(meal.get("sugar", 0))
        totals["sodium_mg"] += int(meal.get("sodium_mg", 0))
        totals["cost_estimate"] += float(meal.get("cost_estimate", 0.0))

    kcal_from_macros = (
        totals["protein"] * 4 +
        totals["carbs"] * 4 +
        totals["fat"] * 9
    )

    macro_pct = {
        "protein_pct": round((totals["protein"] * 4) / totals["calories"] * 100, 1) if totals["calories"] else 0,
        "carbs_pct": round((totals["carbs"] * 4) / totals["calories"] * 100, 1) if totals["calories"] else 0,
        "fat_pct": round((totals["fat"] * 9) / totals["calories"] * 100, 1) if totals["calories"] else 0,
    }

    return {
        "totals": totals,
        "kcal_from_macros_estimate": int(round(kcal_from_macros)),
        "macro_percentages": macro_pct,
    }


# ======================================================
# SCORING
# ======================================================

def nutrition_score(meals: List[Dict], profile: Dict) -> Dict:
    nutrition = calculate_nutrition(meals)
    totals = nutrition["totals"]
    targets = macro_targets(profile)

    score = 100
    reasons = []

    if totals["protein"] < targets["protein_g"] * 0.8:
        score -= 15
        reasons.append("Protein intake is low")

    if totals["fiber"] < 20:
        score -= 10
        reasons.append("Low fiber intake")

    if totals["sugar"] > 60:
        score -= 10
        reasons.append("High sugar intake")

    if totals["sodium_mg"] > 2300:
        score -= 10
        reasons.append("High sodium intake")

    calorie_diff = abs(totals["calories"] - targets["calories"])
    if calorie_diff > targets["calories"] * 0.2:
        score -= 15
        reasons.append("Calories far from target")

    score = _clamp(score, 0, 100)

    return {
        "score": score,
        "reasons": reasons,
    }


# ======================================================
# PORTION ADJUSTMENT
# ======================================================

def portion_adjust(meal: Dict, profile: Dict, intensity: str = "normal") -> Dict:
    scale = 1.0
    goal = _goal(profile)

    if goal == "cut":
        scale -= 0.1
    elif goal == "bulk":
        scale += 0.1

    if intensity == "light":
        scale *= 0.9
    elif intensity == "strong":
        scale *= 1.15

    scale = _clamp(scale, 0.75, 1.3)

    adjusted = meal.copy()
    for key in ["calories", "protein", "carbs", "fat", "fiber", "sugar", "sodium_mg"]:
        adjusted[key] = int(round(meal.get(key, 0) * scale))

    adjusted["portion_scale"] = round(scale, 2)
    return adjusted


# ======================================================
# WHAT-IF SIMULATION
# ======================================================

def what_if(
    profile: Dict,
    meals: List[Dict],
    delta_calories: int = 0,
    delta_protein_g: int = 0,
) -> Dict:
    base_targets = macro_targets(profile)
    nutrition = calculate_nutrition(meals)

    return {
        "base_targets": base_targets,
        "scenario_targets": {
            "calories": base_targets["calories"] + delta_calories,
            "protein_g": base_targets["protein_g"] + delta_protein_g,
        },
        "difference_vs_current": {
            "calories": nutrition["totals"]["calories"] - (base_targets["calories"] + delta_calories),
            "protein_g": nutrition["totals"]["protein"] - (base_targets["protein_g"] + delta_protein_g),
        },
    }


# ======================================================
# DAILY SUMMARY
# ======================================================

def daily_summary(profile: Dict, meals: List[Dict]) -> Dict:
    targets = macro_targets(profile)
    nutrition = calculate_nutrition(meals)
    score = nutrition_score(meals, profile)

    return {
        "targets": targets,
        "totals": nutrition["totals"],
        "macro_percentages": nutrition["macro_percentages"],
        "nutrition_score": score,
    }
