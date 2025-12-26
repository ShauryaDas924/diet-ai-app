import React, { useMemo, useState } from "react";
import { Card, Button, Input, Select, Textarea, Divider, Pill } from "../components/ui.jsx";
import { useProfile } from "../state/profile.jsx";
import { api, apiErrorMessage } from "../api/client.jsx";
import { Target } from "lucide-react";

export default function Profile() {
  const { profile, setProfile, resetProfile } = useProfile();
  const [targets, setTargets] = useState(null);
  const [macros, setMacros] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const profileForApi = useMemo(() => {
    // Backend expects a dict; empty strings are OK but we’ll keep it neat.
    const cleaned = { ...profile };
    if (cleaned.income === "") delete cleaned.income;
    if (cleaned.dietary_preferences === "") delete cleaned.dietary_preferences;
    if (cleaned.allergies === "") delete cleaned.allergies;
    return cleaned;
  }, [profile]);

  async function fetchTargets() {
    setBusy(true);
    setErr("");
    try {
      const [t, m] = await Promise.all([
        api.post("/calorie-target", profileForApi),
        api.post("/macros", profileForApi),
      ]);
      setTargets(t.data);
      setMacros(m.data);
    } catch (e) {
      setErr(apiErrorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="stackLg">
      <div className="pageHead">
        <div>
          <h2 className="h2">Profile</h2>
          <div className="muted">This drives meal planning, targets, scoring, and “what‑if”.</div>
        </div>
        <div className="row">
          <Button variant="secondary" onClick={resetProfile} disabled={busy}>
            Reset
          </Button>
          <Button onClick={fetchTargets} disabled={busy}>
            Get Targets
          </Button>
        </div>
      </div>

      {err && <div className="alert">{err}</div>}

      <div className="grid2">
        <Card title="Basics" subtitle="Used for calorie target + macros">
          <div className="grid2">
            <Input
              label="Age"
              type="number"
              value={profile.age}
              onChange={(e) => setProfile({ ...profile, age: Number(e.target.value) })}
            />
            <Select
              label="Gender"
              value={profile.gender}
              onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
            >
              <option value="male">male</option>
              <option value="female">female</option>
              <option value="other">other</option>
            </Select>

            <Input
              label="Height (cm)"
              type="number"
              value={profile.height_cm ?? ""}
              onChange={(e) => setProfile({ ...profile, height_cm: Number(e.target.value) })}
            />
            <Input
              label="Weight (kg)"
              type="number"
              value={profile.weight_kg ?? ""}
              onChange={(e) => setProfile({ ...profile, weight_kg: Number(e.target.value) })}
            />

            <Select
              label="Activity level"
              value={profile.activity_level}
              onChange={(e) => setProfile({ ...profile, activity_level: e.target.value })}
            >
              <option value="sedentary">sedentary</option>
              <option value="light">light</option>
              <option value="moderate">moderate</option>
              <option value="active">active</option>
              <option value="very_active">very_active</option>
            </Select>

            <Select
              label="Goal"
              value={profile.goal}
              onChange={(e) => setProfile({ ...profile, goal: e.target.value })}
            >
              <option value="cut">cut</option>
              <option value="maintain">maintain</option>
              <option value="bulk">bulk</option>
            </Select>
          </div>

          <Divider />

          <div className="grid2">
            <Textarea
              label="Dietary preferences (optional)"
              placeholder="e.g. vegetarian, halal, keto"
              value={profile.dietary_preferences ?? ""}
              onChange={(e) => setProfile({ ...profile, dietary_preferences: e.target.value })}
            />
            <Textarea
              label="Allergies (optional)"
              placeholder="e.g. peanuts, dairy"
              value={profile.allergies ?? ""}
              onChange={(e) => setProfile({ ...profile, allergies: e.target.value })}
            />
          </div>

          <Divider />

          <div className="grid2">
            <Select
              label="Budget"
              value={profile.budget ?? "medium"}
              onChange={(e) => setProfile({ ...profile, budget: e.target.value })}
            >
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </Select>
            <Input
              label="Income (optional)"
              placeholder="e.g. 40000"
              value={profile.income ?? ""}
              onChange={(e) => setProfile({ ...profile, income: e.target.value })}
            />
          </div>
        </Card>

        <Card
          title="Targets"
          subtitle="From /calorie-target and /macros"
          icon={<Target size={18} />}
        >
          {!targets && !macros ? (
            <div className="muted">Click “Get Targets”.</div>
          ) : (
            <div className="stack">
              {targets && (
                <div className="row rowWrap">
                  <Pill>Target: {targets.target_calories} kcal/day</Pill>
                  {targets.tdee && <Pill>TDEE: {Math.round(targets.tdee)} kcal</Pill>}
                </div>
              )}
              {macros && (
                <div className="row rowWrap">
                  <Pill>Protein: {macros.protein_g}g</Pill>
                  <Pill>Carbs: {macros.carbs_g}g</Pill>
                  <Pill>Fat: {macros.fat_g}g</Pill>
                </div>
              )}
              <div className="muted small">
                These targets feed directly into meal scoring and “what‑if” calculations.
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
