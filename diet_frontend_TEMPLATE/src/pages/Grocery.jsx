import React, { useEffect, useState } from "react";
import { Card, Button, Divider } from "../components/ui.jsx"
import { api, apiErrorMessage } from "../api/client.jsx";
import { loadSession, saveSession } from "../state/session.js";
import { ShoppingBasket } from "lucide-react";

export default function Grocery() {
  const [session] = useState(loadSession());
  const [list, setList] = useState([]);
  const [checked, setChecked] = useState({});
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    saveSession(session);
  }, [session]);

  async function generateList() {
    setBusy(true);
    setErr("");
    try {
      const meals = session.meals || [];
      const res = await api.post("/grocery-list", { meals });
      const items = Array.isArray(res.data) ? res.data : res.data?.items ?? [];
      setList(items);
      setChecked({});
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
          <h2 className="h2">Grocery List</h2>
          <div className="muted">Uses your backend /grocery-list from current meals.</div>
        </div>
        <Button onClick={generateList} disabled={busy || !session.meals}>
          <ShoppingBasket size={16} /> Generate
        </Button>
      </div>

      {err && <div className="alert">{err}</div>}

      <Card title="Items" subtitle={list.length ? `${list.length} items` : "Generate from your meal plan"}>
        {!list.length ? (
          <div className="muted">
            Tip: Generate a meal plan first, then come back here.
          </div>
        ) : (
          <div className="stack">
            <div className="muted small">Tap to check off.</div>
            <Divider />
            <ul className="checklist">
              {list.map((item, idx) => (
                <li key={idx} className="checkItem">
                  <label className="checkLabel">
                    <input
                      type="checkbox"
                      checked={!!checked[idx]}
                      onChange={(e) => setChecked((c) => ({ ...c, [idx]: e.target.checked }))}
                    />
                    <span>{String(item)}</span>
                  </label>
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>
    </div>
  );
}
