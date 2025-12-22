# backend/ai.py
from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any
import os
import json
import random
from dotenv import load_dotenv
from logging_config import logger

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional OpenAI usage (kept isolated so the app still works without it)
_HAS_OPENAI = False
_client = None
if OPENAI_API_KEY:
    try:
        # NOTE: keep this import inside the try so teammates without OpenAI installed can still run locally
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY)
        _HAS_OPENAI = True
    except Exception:
        _HAS_OPENAI = False


# -----------------------------
# Helpers
# -----------------------------

def _lower(x: Any) -> str:
    return str(x).strip().lower() if x is not None else ""

def _safe_list(x: Any) -> List:
    if isinstance(x, list):
        return x
    if isinstance(x, str) and x.strip():
        return [t.strip() for t in x.replace(",", " ").split() if t.strip()]
    return []

def _normalize_goal(profile: Dict) -> str:
    g = _lower(profile.get("goal"))
    if g in {"cut", "lose", "loss", "fat_loss", "deficit"}:
        return "cut"
    if g in {"bulk", "gain", "surplus", "muscle_gain"}:
        return "bulk"
    return "maintain"

def _normalize_budget(profile: Dict) -> str:
    b = _lower(profile.get("budget", ""))
    if b in {"low", "cheap", "student"}:
        return "low"
    if b in {"high", "premium"}:
        return "high"
    income = profile.get("income")
    if isinstance(income, (int, float)):
        if income < 25000:
            return "low"
        if income > 80000:
            return "high"
    return "medium"

def _normalize_prefs(profile: Dict) -> Dict:
    prefs = {_lower(p) for p in _safe_list(profile.get("dietary_preferences", profile.get("preferences", [])))}
    allergies = {_lower(a) for a in _safe_list(profile.get("allergies", []))}
    return {"prefs": prefs, "allergies": allergies}

def _contains_any(text: str, keywords: List[str]) -> bool:
    t = _lower(text)
    return any(k in t for k in keywords)


# -----------------------------
# Your internal meal database (starter)
# -----------------------------
# Real app pattern: start with curated meals; AI can propose variants.

MEAL_DB: List[Dict] = [
    # Breakfast
    {
        "meal_type": "breakfast",
        "name": "Oatmeal with Banana and Peanut Butter",
        "calories": 500, "protein": 18, "carbs": 65, "fat": 18,
        "fiber": 10, "sugar": 14, "sodium_mg": 120,
        "ingredients": ["oats", "banana", "peanut butter", "cinnamon"],
        "cost_estimate": 3.25,
        "allergens": ["peanuts"],
    },
    {
        "meal_type": "breakfast",
        "name": "Egg & Veggie Scramble + Toast",
        "calories": 520, "protein": 28, "carbs": 40, "fat": 26,
        "fiber": 6, "sugar": 6, "sodium_mg": 520,
        "ingredients": ["eggs", "spinach", "peppers", "onion", "bread"],
        "cost_estimate": 4.75,
        "allergens": ["eggs", "gluten"],
    },

    # Lunch
    {
        "meal_type": "lunch",
        "name": "Chicken Rice Bowl",
        "calories": 650, "protein": 45, "carbs": 70, "fat": 16,
        "fiber": 7, "sugar": 8, "sodium_mg": 700,
        "ingredients": ["chicken breast", "rice", "black beans", "salsa", "lettuce"],
        "cost_estimate": 6.50,
        "allergens": [],
    },
    {
        "meal_type": "lunch",
        "name": "Tofu Stir Fry + Rice",
        "calories": 620, "protein": 28, "carbs": 75, "fat": 20,
        "fiber": 9, "sugar": 12, "sodium_mg": 850,
        "ingredients": ["tofu", "rice", "broccoli", "carrots", "soy sauce", "garlic"],
        "cost_estimate": 5.25,
        "allergens": ["soy"],
    },

    # Dinner
    {
        "meal_type": "dinner",
        "name": "Lean Beef Chili",
        "calories": 720, "protein": 48, "carbs": 65, "fat": 24,
        "fiber": 12, "sugar": 9, "sodium_mg": 980,
        "ingredients": ["lean beef", "kidney beans", "tomatoes", "onion", "chili spices"],
        "cost_estimate": 7.50,
        "allergens": [],
    },
    {
        "meal_type": "dinner",
        "name": "Pasta with Marinara + Side Veggies",
        "calories": 700, "protein": 22, "carbs": 95, "fat": 18,
        "fiber": 10, "sugar": 14, "sodium_mg": 780,
        "ingredients": ["pasta", "marinara", "spinach", "parmesan", "olive oil"],
        "cost_estimate": 4.25,
        "allergens": ["gluten", "dairy"],
    },
]


DIET_RULES = {
    "vegetarian": {"forbid": ["chicken", "turkey", "beef", "fish", "salmon"]},
    "vegan": {"forbid": ["chicken", "turkey", "beef", "fish", "salmon", "egg", "eggs", "dairy", "cheese", "yogurt", "honey", "parmesan"]},
    "pescatarian": {"forbid": ["chicken", "turkey", "beef"]},
    "halal": {"forbid": ["pork", "bacon", "ham"]},  # simplified
}


# -----------------------------
# Compliance checks (real-app safety)
# -----------------------------

def diet_compliance_check(meal: Dict, profile: Dict) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    prefs_info = _normalize_prefs(profile)
    prefs = prefs_info["prefs"]
    allergies = prefs_info["allergies"]

    meal_name = _lower(meal.get("name", ""))
    ingredients = [_lower(x) for x in meal.get("ingredients", [])]
    allergens = {_lower(a) for a in meal.get("allergens", [])}

    for a in allergies:
        if a and (a in allergens or a in ingredients or a in meal_name):
            reasons.append(f"contains allergen: {a}")

    for pref in prefs:
        rule = DIET_RULES.get(pref)
        if not rule:
            continue
        forbid = rule.get("forbid", [])
        if _contains_any(meal_name, forbid) or any(any(f in ing for f in forbid) for ing in ingredients):
            reasons.append(f"conflicts with preference: {pref}")

    return (len(reasons) == 0), reasons


# -----------------------------
# Meal selection utilities
# -----------------------------

def _find_by_name(name_lower: str) -> Optional[Dict]:
    for m in MEAL_DB:
        if _lower(m.get("name")) == name_lower:
            return m
    for m in MEAL_DB:
        if name_lower in _lower(m.get("name")):
            return m
    return None

def resolve_meal(meal_in: Any) -> Optional[Dict]:
    if meal_in is None:
        return None
    if isinstance(meal_in, dict):
        if any(k in meal_in for k in ["calories", "protein", "carbs", "fat"]):
            return meal_in
        nm = _lower(meal_in.get("name"))
        return _find_by_name(nm) if nm else None
    if isinstance(meal_in, str):
        return _find_by_name(_lower(meal_in))
    return None

def _meal_payload(label: str, meal: Dict) -> Dict:
    if not meal:
        return {"meal": label, "name": "No meal available"}
    return {
        "meal": label,
        "name": meal.get("name"),
        "calories": int(meal.get("calories", 0)),
        "protein": int(meal.get("protein", 0)),
        "carbs": int(meal.get("carbs", 0)),
        "fat": int(meal.get("fat", 0)),
        "fiber": int(meal.get("fiber", 0)),
        "sugar": int(meal.get("sugar", 0)),
        "sodium_mg": int(meal.get("sodium_mg", 0)),
        "cost_estimate": float(meal.get("cost_estimate", 0.0)),
        "ingredients": meal.get("ingredients", []),
        "allergens": meal.get("allergens", []),
    }

def _matches_budget(meal: Dict, budget_level: str) -> bool:
    cost = float(meal.get("cost_estimate", 0.0))
    if budget_level == "low":
        return cost <= 4.75
    if budget_level == "high":
        return True
    return cost <= 8.00

def filter_meals_for_profile(pool: List[Dict], profile: Dict) -> List[Dict]:
    budget = _normalize_budget(profile)
    out = []
    for m in pool:
        ok, _reasons = diet_compliance_check(m, profile)
        if not ok:
            continue
        if not _matches_budget(m, budget):
            continue
        out.append(m)
    return out

def apply_constraint(pool: List[Dict], constraint: Optional[str]) -> List[Dict]:
    c = _lower(constraint)
    if not c:
        return pool

    if c in {"lower_calories", "low_calories"}:
        return sorted(pool, key=lambda m: int(m.get("calories", 0)))[: max(1, len(pool)//2)]
    if c in {"higher_protein", "high_protein"}:
        return sorted(pool, key=lambda m: int(m.get("protein", 0)), reverse=True)[: max(1, len(pool)//2)]
    if c in {"cheaper", "low_cost", "budget"}:
        return sorted(pool, key=lambda m: float(m.get("cost_estimate", 0.0)))[: max(1, len(pool)//2)]
    if c in {"lower_sodium", "low_sodium"}:
        return sorted(pool, key=lambda m: int(m.get("sodium_mg", 0)))[: max(1, len(pool)//2)]
    if c in {"higher_fiber", "high_fiber"}:
        return sorted(pool, key=lambda m: int(m.get("fiber", 0)), reverse=True)[: max(1, len(pool)//2)]
    if c in {"vegetarian"}:
        return [m for m in pool if not _contains_any(m.get("name", ""), ["chicken", "turkey", "beef", "fish", "salmon"])]
    if c in {"vegan"}:
        return [m for m in pool if not _contains_any(m.get("name", ""), ["chicken", "turkey", "beef", "fish", "salmon", "egg", "yogurt", "parmesan", "cheese", "honey"])]
    return pool

def _seeded_choice(pool: List[Dict], seed: str) -> Dict:
    if not pool:
        return {}
    rnd = random.Random(seed)
    return rnd.choice(pool)


# -----------------------------
# AI calls (optional real AI)
# -----------------------------

def _openai_generate_meal_ideas(profile: Dict) -> Optional[List[Dict]]:
    """
    Real AI hook: return a 3-meal plan JSON.
    If OpenAI is unavailable, return None and we fallback to MEAL_DB logic.
    """
    if not _HAS_OPENAI or _client is None:
        return None

    prefs_info = _normalize_prefs(profile)
    prefs = sorted(list(prefs_info["prefs"]))
    allergies = sorted(list(prefs_info["allergies"]))
    goal = _normalize_goal(profile)
    budget = _normalize_budget(profile)

    prompt = {
        "task": "Generate a 1-day meal plan",
        "constraints": {
            "goal": goal,
            "budget_level": budget,
            "dietary_preferences": prefs,
            "allergies": allergies,
        },
        "required_format": [
            {
                "meal": "Breakfast",
                "name": "string",
                "ingredients": ["string", "..."],
                "calories": "int",
                "protein": "int",
                "carbs": "int",
                "fat": "int",
                "fiber": "int optional",
                "sugar": "int optional",
                "sodium_mg": "int optional",
                "cost_estimate": "float"
            }
        ]
    }

    try:
        resp = _client.responses.create(
            model="gpt-4.1-mini",
            input=f"Return ONLY valid JSON.\n\n{json.dumps(prompt)}",
        )
        text = resp.output_text.strip()
        data = json.loads(text)
        if isinstance(data, list) and len(data) >= 3:
            return data[:3]
        return None
    except Exception:
        return None


# -----------------------------
# Public feature functions
# -----------------------------

def generate_meal_plan(user_profile: Dict) -> List[Dict]:
    logger.info("generate_meal_plan called")
    """
    Real-app behavior:
    - Try AI (if configured)
    - Otherwise use curated DB + rules
    """
    ai_plan = _openai_generate_meal_ideas(user_profile)
    if ai_plan:
        logger.info("AI-generated meal plan accepted")
        # Ensure basic safety check before returning
        safe = []
        for m in ai_plan:
            ok, _ = diet_compliance_check(m, user_profile)
            if ok:
                safe.append(m)
        if len(safe) >= 3:
            return safe[:3]
        # fall back if AI output conflicts with allergies/prefs
        # (keeps UX predictable)
    # DB fallback:
    seed = _lower(user_profile.get("user_id") or user_profile.get("email") or "default")

    b_pool = filter_meals_for_profile([m for m in MEAL_DB if m["meal_type"] == "breakfast"], user_profile)
    l_pool = filter_meals_for_profile([m for m in MEAL_DB if m["meal_type"] == "lunch"], user_profile)
    d_pool = filter_meals_for_profile([m for m in MEAL_DB if m["meal_type"] == "dinner"], user_profile)

    # If too strict, relax to diet/allergy only (budget relaxed)
    def relax(pool: List[Dict], meal_type: str) -> List[Dict]:
        if pool:
            return pool
        raw = [m for m in MEAL_DB if m["meal_type"] == meal_type]
        safe = []
        for m in raw:
            ok, _ = diet_compliance_check(m, user_profile)
            if ok:
                safe.append(m)
        return safe or raw

    b_pool = relax(b_pool, "breakfast")
    l_pool = relax(l_pool, "lunch")
    d_pool = relax(d_pool, "dinner")

    return [
        _meal_payload("Breakfast", _seeded_choice(b_pool, seed + ":b")),
        _meal_payload("Lunch", _seeded_choice(l_pool, seed + ":l")),
        _meal_payload("Dinner", _seeded_choice(d_pool, seed + ":d")),
    ]


def generate_weekly_meal_plan(user_profile: Dict) -> List[Dict]:
    week = []
    base_id = _lower(user_profile.get("user_id") or "user")
    for day in range(1, 8):
        shifted = {**user_profile, "user_id": f"{base_id}-day{day}"}
        week.append({"day": day, "meals": generate_meal_plan(shifted)})
    return week


def meal_regenerate(payload: Dict) -> Dict:
    profile = payload.get("user_profile", {}) or {}
    meal_type_in = _lower(payload.get("meal_type", "dinner"))
    constraint = payload.get("constraint")

    if meal_type_in in {"breakfast", "b"}:
        meal_type = "breakfast"; label = "Breakfast"
    elif meal_type_in in {"lunch", "l"}:
        meal_type = "lunch"; label = "Lunch"
    else:
        meal_type = "dinner"; label = "Dinner"

    pool = filter_meals_for_profile([m for m in MEAL_DB if m["meal_type"] == meal_type], profile)
    pool = apply_constraint(pool, constraint) or pool

    seed = _lower(profile.get("user_id") or "user") + f":regen:{meal_type}:{_lower(constraint)}"
    chosen = _seeded_choice(pool, seed) if pool else {}
    ok, reasons = diet_compliance_check(chosen, profile) if chosen else (False, ["no meal available"])

    return {
        "meal_type": label,
        "constraint": constraint,
        "meal": _meal_payload(label, chosen) if ok else {"meal": label, "name": "No compliant meal found", "reasons": reasons},
    }


def swap_meal(payload: Dict) -> Dict:
    profile = payload.get("user_profile", {}) or {}
    meal_in = _lower(payload.get("meal", "dinner"))
    constraint = payload.get("constraint")

    if meal_in in {"breakfast", "b"}:
        meal_type = "breakfast"; label = "Breakfast"
    elif meal_in in {"lunch", "l"}:
        meal_type = "lunch"; label = "Lunch"
    else:
        meal_type = "dinner"; label = "Dinner"

    pool = filter_meals_for_profile([m for m in MEAL_DB if m["meal_type"] == meal_type], profile)
    pool = apply_constraint(pool, constraint) or pool

    seed = _lower(profile.get("user_id") or "user") + f":swap:{meal_type}:{_lower(constraint)}"
    chosen = _seeded_choice(pool, seed) if pool else {}

    return {
        "meal": label,
        "new_meal": _meal_payload(label, chosen),
        "reason": "Swapped based on your constraint and preferences.",
    }


def compare_meals(payload: Dict) -> Dict:
    a = resolve_meal(payload.get("meal_a"))
    b = resolve_meal(payload.get("meal_b"))
    if not a or not b:
        return {"error": "Unable to resolve one or both meals"}

    def summary(m: Dict) -> Dict:
        return {
            "name": m.get("name"),
            "calories": int(m.get("calories", 0)),
            "protein": int(m.get("protein", 0)),
            "carbs": int(m.get("carbs", 0)),
            "fat": int(m.get("fat", 0)),
            "fiber": int(m.get("fiber", 0)),
            "sodium_mg": int(m.get("sodium_mg", 0)),
            "cost_estimate": float(m.get("cost_estimate", 0.0)),
        }

    highlights = []
    if int(a.get("calories", 0)) < int(b.get("calories", 0)):
        highlights.append("A is lower calorie")
    elif int(b.get("calories", 0)) < int(a.get("calories", 0)):
        highlights.append("B is lower calorie")

    if int(a.get("protein", 0)) > int(b.get("protein", 0)):
        highlights.append("A is higher protein")
    elif int(b.get("protein", 0)) > int(a.get("protein", 0)):
        highlights.append("B is higher protein")

    if float(a.get("cost_estimate", 0.0)) < float(b.get("cost_estimate", 0.0)):
        highlights.append("A is cheaper")
    elif float(b.get("cost_estimate", 0.0)) < float(a.get("cost_estimate", 0.0)):
        highlights.append("B is cheaper")

    return {"meal_a": summary(a), "meal_b": summary(b), "highlights": highlights}


def explain_meal_choice(payload: Dict) -> Dict:
    profile = payload.get("user_profile", {}) or {}
    meal = resolve_meal(payload.get("meal"))
    if not meal:
        return {"explanation": "Meal not found. Provide a meal object or known meal name."}

    goal = _normalize_goal(profile)
    budget = _normalize_budget(profile)
    prefs_info = _normalize_prefs(profile)
    prefs = sorted(list(prefs_info["prefs"])) if prefs_info["prefs"] else []
    allergies = sorted(list(prefs_info["allergies"])) if prefs_info["allergies"] else []

    ok, reasons = diet_compliance_check(meal, profile)

    lines = [
        f"Goal fit: {goal}.",
        f"Macros: ~{meal.get('protein')}g protein, ~{meal.get('calories')} kcal.",
        f"Budget: estimated cost ${meal.get('cost_estimate')} (budget level {budget}).",
    ]
    if prefs:
        lines.append(f"Preferences considered: {', '.join(prefs)}.")
    if allergies:
        lines.append("Allergy rules applied.")
    if not ok:
        lines.append(f"Warning: compliance issues: {', '.join(reasons)}.")

    return {"explanation": " ".join(lines)}


def generate_grocery_list(meals: List[Dict]) -> Dict:
    items = []
    missing = []
    for m in meals or []:
        resolved = resolve_meal(m) or m
        ings = resolved.get("ingredients")
        if not ings:
            missing.append(resolved.get("name", str(m)))
            continue
        items.extend([_lower(i) for i in ings if i])

    unique = sorted(set(items))
    return {"items": unique, "missing": missing, "count": len(unique)}
