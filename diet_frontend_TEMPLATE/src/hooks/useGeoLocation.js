import { useEffect, useState } from "react";

export function useGeoLocation() {
  const [state, setState] = useState({
    status: "idle", // idle | loading | ready | error
    lat: null,
    lng: null,
    error: null,
  });

  useEffect(() => {
    if (!navigator.geolocation) {
      setState({ status: "error", lat: null, lng: null, error: "Geolocation not supported" });
      return;
    }
    setState((s) => ({ ...s, status: "loading" }));
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setState({
          status: "ready",
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          error: null,
        });
      },
      (err) => {
        setState({ status: "error", lat: null, lng: null, error: err.message || "Location denied" });
      },
      { enableHighAccuracy: true, timeout: 10_000 }
    );
  }, []);

  return state;
}
