const KEY = "diet_ai_session_v1";

export function loadSession() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : { meals: null, nutrition: null, nutrition_score: null };
  } catch {
    return { meals: null, nutrition: null, nutrition_score: null };
  }
}

export function saveSession(session) {
  try {
    localStorage.setItem(KEY, JSON.stringify(session));
  } catch {
    // ignore
  }
}
