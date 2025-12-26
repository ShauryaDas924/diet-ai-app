import React, { useMemo, useState } from "react";
import { Card, Button, Input, Divider, Pill } from "../components/ui.jsx";
import { useProfile } from "../state/profile.jsx";
import { loadSession } from "../state/session.js";
import { api, apiErrorMessage } from "../api/client.jsx";
import { Shuffle } from "lucide-react";

export default function WhatIf() {
  const { profile } = useProfile();
  const session = loadSession();
  const meals = session.meals || [];
  const [deltaCalories, setDeltaCalories] = useState(0);
  const [deltaProtein, setDeltaProtein] = useState(0);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [result, setResult] = useState(null);
  const [summary, setSummary] = useState(null);

  const disabled = !Array.isArray(meals) || meals.length === 0;

  async function run() {
    setBusy(true);
    setErr("");
    setResult(null);
    setSummary(null);
    try {
      const payload = {
        user_profile: profile,
        meals,
        delta_calories: Number(deltaCalories) || 0,
        delta_protein_g: Number(deltaProtein) || 0,
      };
      const res = await api.post("/what-if", payload);
      const sum = await api.post("/daily-summary", payload);
      setResult(res.data);
      setSummary(sum.data);
    } catch (e) {
      setErr(apiErrorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  const pills = useMemo(() => {
    if (!result) return null;
    const out = [];
    if (result?.new_target_calories != null) out.push(`New target: ${result.new_target_calories} kcal`);
    if (result?.protein_target_g != null) out.push(`Protein target: ${result.protein_target_g}g`);
    if (result?.note) out.push(String(result.note));
    return out;
  }, [result]);

  return (
    <div className="stackLg">
      <div className="pageHead">
        <div>
          <h2 className="h2">What‑If</h2>
          <div className="muted">Small changes, clear feedback (from /what-if and /daily-summary).</div>
        </div>
        <Button onClick={run} disabled={busy || disabled}>
          <Shuffle size={16} /> Run
        </Button>
      </div>

      {disabled && <div className="info">Generate a meal plan first so we can run “what‑if”.</div>}
      {err && <div className="alert">{err}</div>}

      <div className="grid2">
        <Card title="Adjustments" subtitle="Try a small change first">
          <div className="grid2">
            <Input
              label="Δ Calories"
              type="number"
              value={deltaCalories}
              onChange={(e) => setDeltaCalories(e.target.value)}
            />
            <Input
              label="Δ Protein (g)"
              type="number"
              value={deltaProtein}
              onChange={(e) => setDeltaProtein(e.target.value)}
            />
          </div>
          <Divider />
          <div className="muted small">
            This is intentionally simple: the user sees the “so what” without a wall of nutrition math.
          </div>
        </Card>

        <Card title="Result" subtitle="What your backend says">
          {!result && !summary ? (
            <div className="muted">Run a scenario.</div>
          ) : (
            <div className="stack">
              {pills && (
                <div className="row rowWrap">
                  {pills.map((p, i) => (
                    <Pill key={i}>{p}</Pill>
                  ))}
                </div>
              )}
              {summary && (
                <>
                  <Divider />
                  <div className="muted small">Daily summary</div>
                  <pre className="pre">{JSON.stringify(summary, null, 2)}</pre>
                </>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
