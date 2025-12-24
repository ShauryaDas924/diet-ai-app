import React, { useEffect, useMemo, useState } from "react";
import { Card, Button, Input, Select, Divider, Pill }from "../components/ui.jsx";
import MealCard from "../components/MealCard.jsx";
import { api, apiErrorMessage }from "../api/client.jsx";
import { useProfile } from "../state/profile.jsx";
import { loadSession, saveSession } from "../state/session.js";
import { Sparkles, RefreshCcw } from "lucide-react";

export default function MealPlan() {
  const { profile } = useProfile();
  const [session, setSession] = useState(loadSession());
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [constraint, setConstraint] = useState("");
  const [swapMealName, setSwapMealName] = useState("Dinner");

  useEffect(() => {
    saveSession(session);
  }, [session]);

  const meals = session.meals || [];
  const nutrition = session.nutrition;
  const nutritionScore = session.nutrition_score;

  const hasMeals = Array.isArray(meals) && meals.length > 0;

  async function generate() {
    setBusy(true);
    setErr("");
    try {
      const res = await api.post("/meal-plan", { user_profile: profile });
      setSession({
        meals: res.data.meals ?? [],
        nutrition: res.data.nutrition ?? null,
        nutrition_score: res.data.nutrition_score ?? null,
      });
    } catch (e) {
      setErr(apiErrorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  async function swapMeal() {
    setBusy(true);
    setErr("");
    try {
      const res = await api.post("/meal-swap", {
        user_profile: profile,
        meal: swapMealName,
        constraint: constraint || null,
      });
      // swap response shape depends on backend; we handle a few common shapes
      const nextMeals = res.data?.meals ?? res.data ?? meals;
      const computed = await api.post("/nutrition", { meals: nextMeals });
      const score = await api.post("/nutrition-score", { ...profile, meals: undefined }).catch(() => null); // optional; backend signature is profile + MealsPayload; kept best-effort

      setSession((s) => ({
        ...s,
        meals: nextMeals,
        nutrition: computed.data,
        nutrition_score: score?.data ?? s.nutrition_score,
      }));
    } catch (e) {
      setErr(apiErrorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  async function regenerateMeal(mealObj) {
    const mealType = (mealObj?.meal_type || mealObj?.type || mealObj?.meal || "dinner").toString();
    setBusy(true);
    setErr("");
    try {
      const res = await api.post("/meal-regenerate", {
        user_profile: profile,
        meal_type: mealType,
        constraint: constraint || null,
      });

      const replacement = res.data?.meal ?? res.data;
      const nextMeals = meals.map((m) => {
        const mt = (m?.meal_type || m?.type || m?.meal || "").toString().toLowerCase();
        if (mt === mealType.toLowerCase()) return replacement;
        return m;
      });

      const computed = await api.post("/nutrition", { meals: nextMeals });
      setSession((s) => ({ ...s, meals: nextMeals, nutrition: computed.data }));
    } catch (e) {
      setErr(apiErrorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  async function swapFromCard(mealObj) {
    const mt = (mealObj?.meal_type || mealObj?.type || mealObj?.meal || "Dinner").toString();
    setSwapMealName(mt);
    await swapMeal();
  }

  const summaryPills = useMemo(() => {
    if (!nutrition) return null;
    const kcal = nutrition?.total_calories ?? nutrition?.calories ?? null;
    const p = nutrition?.total_protein_g ?? nutrition?.protein_g ?? null;
    const c = nutrition?.total_carbs_g ?? nutrition?.carbs_g ?? null;
    const f = nutrition?.total_fat_g ?? nutrition?.fat_g ?? null;

    return (
      <div className="row rowWrap">
        {kcal != null && <Pill>{Math.round(Number(kcal))} kcal/day</Pill>}
        {p != null && <Pill>{Math.round(Number(p))}g protein</Pill>}
        {c != null && <Pill>{Math.round(Number(c))}g carbs</Pill>}
        {f != null && <Pill>{Math.round(Number(f))}g fat</Pill>}
        {nutritionScore != null && <Pill>Score: {Math.round(Number(nutritionScore))}</Pill>}
      </div>
    );
  }, [nutrition, nutritionScore]);

  return (
    <div className="stackLg">
      <div className="pageHead">
        <div>
          <h2 className="h2">Meal Plan</h2>
          <div className="muted">Generated from your backend /meal-plan. Swap/regenerate are optional.</div>
        </div>
        <div className="row">
          <Button onClick={generate} disabled={busy}>
            <Sparkles size={16} /> Generate
          </Button>
          {hasMeals && (
            <Button variant="secondary" onClick={() => setSession({ meals: null, nutrition: null, nutrition_score: null })} disabled={busy}>
              Clear
            </Button>
          )}
        </div>
      </div>

      {err && <div className="alert">{err}</div>}

      <Card title="Controls" subtitle="Optional constraints">
        <div className="grid3">
          <Input
            label="Constraint (optional)"
            placeholder="e.g. high protein, cheap, no dairy"
            value={constraint}
            onChange={(e) => setConstraint(e.target.value)}
          />
          <Select label="Swap meal" value={swapMealName} onChange={(e) => setSwapMealName(e.target.value)}>
            <option value="Breakfast">Breakfast</option>
            <option value="Lunch">Lunch</option>
            <option value="Dinner">Dinner</option>
          </Select>
          <div className="field">
            <span className="fieldLabel">Swap action</span>
            <Button variant="secondary" onClick={swapMeal} disabled={busy || !hasMeals}>
              <RefreshCcw size={16} /> Swap selected
            </Button>
            <span className="fieldHint">Uses /meal-swap with your current profile.</span>
          </div>
        </div>
        {summaryPills && (
          <>
            <Divider />
            {summaryPills}
          </>
        )}
      </Card>

      <div className="grid2">
        {hasMeals ? (
          meals.map((m, idx) => (
            <MealCard
              key={idx}
              meal={m}
              onSwap={swapFromCard}
              onRegenerate={regenerateMeal}
            />
          ))
        ) : (
          <Card title="No meals yet" subtitle="Click Generate to create a plan.">
            <div className="muted">
              The frontend intentionally shows only the user-facing outputs of the backend.
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
