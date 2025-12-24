import React, { useState } from "react";
import { Card, Button, Pill, Divider } from "../components/ui.jsx"
import { api, apiErrorMessage } from "../api/client.jsx";
import { useProfile } from "../state/profile.jsx";
import { Info, ShieldCheck } from "lucide-react";

export default function MealCard({ meal, onSwap, onRegenerate }) {
  const { profile } = useProfile();
  const [busy, setBusy] = useState(false);
  const [compliance, setCompliance] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const title = meal?.name || meal?.meal || meal?.type || "Meal";
  const mealType = meal?.meal_type || meal?.type || meal?.meal || "";

  async function checkCompliance() {
    setBusy(true);
    setCompliance(null);
    try {
      const res = await api.post("/diet-compliance", {
        user_profile: profile,
        meal,
      });
      setCompliance(res.data);
    } catch (e) {
      setCompliance({ ok: false, reasons: [apiErrorMessage(e)] });
    } finally {
      setBusy(false);
    }
  }

  async function explain() {
    setBusy(true);
    setExplanation(null);
    try {
      const res = await api.post("/meal-explanation", {
        user_profile: profile,
        meal,
      });
      setExplanation(res.data);
    } catch (e) {
      setExplanation({ error: apiErrorMessage(e) });
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card
      title={title}
      subtitle={mealType ? mealType.toString() : undefined}
      icon={<Info size={18} />}
      footer={
        <div className="row rowWrap">
          <Button variant="secondary" onClick={() => onSwap?.(meal)} disabled={busy}>
            Swap
          </Button>
          <Button variant="secondary" onClick={() => onRegenerate?.(meal)} disabled={busy}>
            Regenerate
          </Button>
          <Button variant="ghost" onClick={checkCompliance} disabled={busy}>
            <ShieldCheck size={16} /> Compliance
          </Button>
          <Button variant="ghost" onClick={explain} disabled={busy}>
            Explain
          </Button>
        </div>
      }
    >
      <div className="stack">
        {meal?.calories != null && (
          <div className="row rowWrap">
            <Pill>{Math.round(Number(meal.calories))} kcal</Pill>
            {meal?.protein_g != null && <Pill>{Math.round(Number(meal.protein_g))}g protein</Pill>}
            {meal?.carbs_g != null && <Pill>{Math.round(Number(meal.carbs_g))}g carbs</Pill>}
            {meal?.fat_g != null && <Pill>{Math.round(Number(meal.fat_g))}g fat</Pill>}
          </div>
        )}

        {Array.isArray(meal?.ingredients) && meal.ingredients.length > 0 && (
          <div>
            <div className="muted small">Ingredients</div>
            <div className="chips">
              {meal.ingredients.slice(0, 12).map((ing, idx) => (
                <span className="chip" key={idx}>
                  {ing}
                </span>
              ))}
            </div>
          </div>
        )}

        {(compliance || explanation) && <Divider />}

        {compliance && (
          <div className="stack">
            <div className={compliance.ok ? "okText" : "warnText"}>
              {compliance.ok ? "Fits your profile" : "May not fit your profile"}
            </div>
            {Array.isArray(compliance.reasons) && (
              <ul className="list">
                {compliance.reasons.slice(0, 6).map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {explanation && (
          <div className="stack">
            {explanation.error ? (
              <div className="warnText">{explanation.error}</div>
            ) : (
              <div className="small">{String(explanation)}</div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
