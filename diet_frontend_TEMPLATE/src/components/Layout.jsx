import React from "react";
import { NavLink } from "react-router-dom";
import { Salad, MapPinned, Sparkles, User, ShoppingBasket, Shuffle } from "lucide-react";

export default function Layout({ children }) {
  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brandMark" aria-hidden="true" />
          <div>
            <div className="brandTitle">Diet AI</div>
            <div className="brandSub">Meal plans • Nutrition • Store map</div>
          </div>
        </div>

        <nav className="nav">
          <NavItem to="/" icon={<Sparkles size={18} />} label="Home" />
          <NavItem to="/profile" icon={<User size={18} />} label="Profile" />
          <NavItem to="/meal-plan" icon={<Salad size={18} />} label="Meal Plan" />
          <NavItem to="/grocery" icon={<ShoppingBasket size={18} />} label="Grocery" />
          <NavItem to="/stores" icon={<MapPinned size={18} />} label="Stores" />
          <NavItem to="/what-if" icon={<Shuffle size={18} />} label="What‑If" />
        </nav>
      </header>

      <main className="content">
        <div className="container">{children}</div>
      </main>

      <footer className="footer">
        <span>Minimal • Blue/White • Frontend driven by your backend endpoints</span>
      </footer>
    </div>
  );
}

function NavItem({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => "navItem" + (isActive ? " navItemActive" : "")}
    >
      <span className="navIcon">{icon}</span>
      <span className="navLabel">{label}</span>
    </NavLink>
  );
}
