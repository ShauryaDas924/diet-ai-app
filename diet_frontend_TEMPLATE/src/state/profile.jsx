import React, { createContext, useContext, useMemo, useState } from "react";

const ProfileContext = createContext(null);

const STORAGE_KEY = "diet_ai_profile_v1";

function loadProfile() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveProfile(profile) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
  } catch {
    // ignore
  }
}

const DEFAULT_PROFILE = {
  age: 20,
  gender: "male",
  height_cm: 175,
  weight_kg: 70,
  activity_level: "moderate",
  goal: "maintain",
  dietary_preferences: "",
  allergies: "",
  budget: "medium",
  income: "",
};

export function ProfileProvider({ children }) {
  const [profile, setProfile] = useState(loadProfile() ?? DEFAULT_PROFILE);

  const value = useMemo(() => {
    return {
      profile,
      setProfile: (next) => {
        setProfile((prev) => {
          const resolved = typeof next === "function" ? next(prev) : next;
          saveProfile(resolved);
          return resolved;
        });
      },
      resetProfile: () => {
        saveProfile(DEFAULT_PROFILE);
        setProfile(DEFAULT_PROFILE);
      },
    };
  }, [profile]);

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
  const ctx = useContext(ProfileContext);
  if (!ctx) throw new Error("useProfile must be used inside ProfileProvider");
  return ctx;
}
