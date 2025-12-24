import React, { useMemo, useState } from "react";
import { Card, Button, Input, Divider, Pill } from "../components/ui.jsx"
import MapView from "../components/MapView.jsx";
import { api, apiErrorMessage } from "../api/client.jsx";
import { useGeoLocation } from "../hooks/useGeoLocation.js";
import { loadSession } from "../state/session.js";
import { MapPinned, LocateFixed } from "lucide-react";

export default function Stores() {
  const geo = useGeoLocation();
  const session = loadSession();
  const [radiusKm, setRadiusKm] = useState(5);
  const [stores, setStores] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const center = useMemo(() => {
    if (geo.status !== "ready") return null;
    return { lat: geo.lat, lng: geo.lng };
  }, [geo]);

  async function fetchStores() {
    if (!center) return;
    setBusy(true);
    setErr("");
    try {
      const res = await api.get("/stores", { params: { lat: center.lat, lng: center.lng, radius_km: radiusKm } });
      setStores(Array.isArray(res.data) ? res.data : []);
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
          <h2 className="h2">Stores</h2>
          <div className="muted">
            Uses /stores (Google Places via your backend) and shows results on a map.
          </div>
        </div>
        <div className="row">
          <Button onClick={fetchStores} disabled={busy || geo.status !== "ready"}>
            <MapPinned size={16} /> Find Stores
          </Button>
        </div>
      </div>

      {geo.status === "loading" && <div className="info">Getting your location…</div>}
      {geo.status === "error" && <div className="alert">{geo.error}</div>}
      {err && <div className="alert">{err}</div>}

      <div className="grid2">
        <Card title="Map" subtitle="Your location + nearby stores">
          <div className="row rowWrap">
            <label className="inlineField">
              <span className="muted small">Radius (km)</span>
              <input
                className="input"
                type="number"
                min="1"
                max="25"
                value={radiusKm}
                onChange={(e) => setRadiusKm(Number(e.target.value))}
                style={{ width: 120 }}
              />
            </label>
            <Button variant="secondary" onClick={fetchStores} disabled={busy || geo.status !== "ready"}>
              <LocateFixed size={16} /> Refresh
            </Button>
          </div>
          <Divider />
          <MapView center={center} radiusKm={radiusKm} stores={stores} />
        </Card>

        <Card
          title="Recommendations"
          subtitle={stores.length ? `${stores.length} stores found` : "Tap “Find Stores”"}
        >
          {!stores.length ? (
            <div className="muted">
              This page is intentionally user-facing: map + simple recommendation reasons (from backend).
            </div>
          ) : (
            <div className="stack">
              {stores.slice(0, 10).map((s) => (
                <StoreRow key={s.place_id || s.name} store={s} />
              ))}
              {session.meals && (
                <div className="muted small">
                  Note: Your backend can score stores more deeply when meal data is provided (ingredient coverage). In this UI,
                  the map stays simple and fast.
                </div>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

function StoreRow({ store }) {
  return (
    <div className="storeRow">
      <div className="storeMain">
        <div className="strong">{store.name}</div>
        <div className="muted small">
          {store.distance_km != null ? `${store.distance_km.toFixed(2)} km` : ""}{" "}
          {store.open_now != null ? (store.open_now ? "• Open" : "• Closed") : ""}
        </div>
        {store.why_recommended && <div className="small">{store.why_recommended}</div>}
      </div>
      <div className="storeMeta">
        {store.meal_plan_support_score != null && (
          <Pill>{Math.round(store.meal_plan_support_score)}</Pill>
        )}
      </div>
    </div>
  );
}
