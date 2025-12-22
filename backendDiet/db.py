# backend/db.py
from __future__ import annotations

import sqlite3
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

# -----------------------------
# Database location
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "diet_app.db"


# -----------------------------
# Connection helper
# -----------------------------

def get_db() -> sqlite3.Connection:
    """
    Returns a SQLite connection.
    Row factory lets us access columns by name.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Initialization
# -----------------------------

def init_db():
    """
    Create tables if they don't exist.
    Safe to call multiple times.
    """
    conn = get_db()
    cur = conn.cursor()

    # -------------------------
    # Users
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE,
        profile_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -------------------------
    # Meal plans (daily)
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS meal_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        date TEXT NOT NULL,
        meals_json TEXT NOT NULL,
        nutrition_json TEXT,
        score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -------------------------
    # Weekly meal plans
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS weekly_meal_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        week_start TEXT NOT NULL,
        plan_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -------------------------
    # Saved meals
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS saved_meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        meal_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -------------------------
    # Grocery lists
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS grocery_lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        date TEXT NOT NULL,
        items_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# User operations
# -----------------------------

def upsert_user(user_id: str, profile: Dict[str, Any]):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (user_id, profile_json)
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        profile_json = excluded.profile_json
    """, (user_id, json.dumps(profile)))

    conn.commit()
    conn.close()


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT profile_json FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None
    return json.loads(row["profile_json"])


# -----------------------------
# Meal plan operations
# -----------------------------

def save_daily_meal_plan(
    user_id: str,
    date: str,
    meals: List[Dict],
    nutrition: Dict,
    score: float,
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO meal_plans (user_id, date, meals_json, nutrition_json, score)
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        date,
        json.dumps(meals),
        json.dumps(nutrition),
        score,
    ))

    conn.commit()
    conn.close()


def get_meal_plans(user_id: str) -> List[Dict]:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT date, meals_json, nutrition_json, score
    FROM meal_plans
    WHERE user_id = ?
    ORDER BY date DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "date": row["date"],
            "meals": json.loads(row["meals_json"]),
            "nutrition": json.loads(row["nutrition_json"]) if row["nutrition_json"] else None,
            "score": row["score"],
        }
        for row in rows
    ]


# -----------------------------
# Weekly plan operations
# -----------------------------

def save_weekly_plan(user_id: str, week_start: str, plan: Dict):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO weekly_meal_plans (user_id, week_start, plan_json)
    VALUES (?, ?, ?)
    """, (user_id, week_start, json.dumps(plan)))

    conn.commit()
    conn.close()


# -----------------------------
# Grocery list operations
# -----------------------------

def save_grocery_list(user_id: str, date: str, items: List[str]):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO grocery_lists (user_id, date, items_json)
    VALUES (?, ?, ?)
    """, (user_id, date, json.dumps(items)))

    conn.commit()
    conn.close()


def get_grocery_lists(user_id: str) -> List[Dict]:
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT date, items_json
    FROM grocery_lists
    WHERE user_id = ?
    ORDER BY date DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "date": row["date"],
            "items": json.loads(row["items_json"]),
        }
        for row in rows
    ]
