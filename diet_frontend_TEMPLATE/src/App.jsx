import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Profile from "./pages/Profile.jsx";
import MealPlan from "./pages/MealPlan.jsx";
import Grocery from "./pages/Grocery.jsx";
import Stores from "./pages/Stores.jsx";
import WhatIf from "./pages/WhatIf.jsx";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/meal-plan" element={<MealPlan />} />
        <Route path="/grocery" element={<Grocery />} />
        <Route path="/stores" element={<Stores />} />
        <Route path="/what-if" element={<WhatIf />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
