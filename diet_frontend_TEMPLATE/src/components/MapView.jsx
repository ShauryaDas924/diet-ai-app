import React, { useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix default marker icons for Vite
// (Leaflet expects these images to be available at runtime.)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

export default function MapView({ center, radiusKm = 5, stores = [] }) {
  const safeCenter = useMemo(() => {
    if (!center?.lat || !center?.lng) return { lat: 0, lng: 0 };
    return center;
  }, [center]);

  return (
    <div className="mapWrap">
      <MapContainer
        center={[safeCenter.lat, safeCenter.lng]}
        zoom={13}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {safeCenter.lat !== 0 && safeCenter.lng !== 0 && (
          <>
            <Marker position={[safeCenter.lat, safeCenter.lng]}>
              <Popup>Your location</Popup>
            </Marker>

            <Circle
              center={[safeCenter.lat, safeCenter.lng]}
              radius={radiusKm * 1000}
              pathOptions={{}}
            />
          </>
        )}

        {stores.map((s) => (
          <Marker
            key={s.place_id || s.name}
            position={[s.lat, s.lng]}
          >
            <Popup>
              <div className="stack">
                <div className="strong">{s.name}</div>
                <div className="muted small">
                  {s.distance_km != null ? `${s.distance_km.toFixed(2)} km away` : ""}
                </div>
                {s.why_recommended && <div className="small">{s.why_recommended}</div>}
                {s.meal_plan_support_score != null && (
                  <div className="pill">{Math.round(s.meal_plan_support_score)} score</div>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
