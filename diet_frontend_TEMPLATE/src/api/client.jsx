import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

export function apiErrorMessage(err) {
  const detail =
    err?.response?.data?.detail ??
    err?.response?.data?.message ??
    err?.message ??
    "Unknown error";
  return typeof detail === "string" ? detail : JSON.stringify(detail);
}
