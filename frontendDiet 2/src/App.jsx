import { Routes, Route } from "react-router-dom";

function Home() {
  return <h1>HOME WORKS</h1>;
}

function Dashboard() {
  return <h1>DASHBOARD WORKS</h1>;
}

function Meals() {
  return <h1>MEALS WORKS</h1>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/meals" element={<Meals />} />
      <Route path="*" element={<h1>404</h1>} />
    </Routes>
  );
}