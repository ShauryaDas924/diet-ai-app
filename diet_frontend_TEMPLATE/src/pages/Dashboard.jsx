import React from "react";
import { Link } from "react-router-dom";
import { Card, Button } from "../components/ui.jsx";
import { Salad, MapPinned, Target, ShoppingBasket, Shuffle, User } from "lucide-react";
import { useProfile } from "../state/profile.jsx";

export default function Dashboard() {
  const { profile } = useProfile();

  return (
    <div className="stackLg">
      <div className="hero">
        <div>
          <h1 className="h1">App Features</h1>
          <p className="sub">
            Minimal blue/white UI. Features are wired to your backend: meal planning, nutrition targets,
            grocery list, and store discovery on a map.
          </p>
        </div>
        <div className="heroRight">
          <div className="heroBadge">
            Profile: <span className="strong">{profile.goal}</span> • <span className="strong">{profile.activity_level}</span>
          </div>
        </div>
      </div>

      <div className="grid4">
        <FeatureCard
          icon={<User size={28} />}
          title="Profile + Targets"
          desc="Set your goal and get calorie + macro targets."
          cta="Edit Profile"
          to="/profile"
        />
        <FeatureCard
          icon={<Salad size={28} />}
          title="Meal Plan (AI)"
          desc="Generate a plan, swap meals, regenerate a meal, and check compliance."
          cta="Open Meal Plan"
          to="/meal-plan"
        />
        <FeatureCard
          icon={<ShoppingBasket size={28} />}
          title="Grocery List"
          desc="Turn your current meals into a simple grocery list."
          cta="Open Grocery"
          to="/grocery"
        />
        <FeatureCard
          icon={<MapPinned size={28} />}
          title="Store Map"
          desc="Find nearby grocery stores and see recommendations on a map."
          cta="Open Stores"
          to="/stores"
        />
      </div>

      <div className="grid2">
        <Card
          title="What‑If"
          subtitle="Adjust calories/protein and see the impact."
          icon={<Shuffle size={18} />}
          footer={
            <Link to="/what-if">
              <Button>Run What‑If</Button>
            </Link>
          }
        >
          <div className="muted">
            This uses your backend /what-if and /daily-summary endpoints to keep the feedback simple for users.
          </div>
        </Card>

        <Card
          title="Design note"
          subtitle="Why the UI looks this way"
          icon={<Target size={18} />}
        >
          <ul className="list">
            <li>Blue + white minimal layout (matches your reference).</li>
            <li>Users see only what’s actionable: plans, targets, grocery, map.</li>
            <li>Advanced intelligence stays behind “Explain / Compliance / What‑If”.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, desc, cta, to }) {
  return (
    <Card
      title={title}
      subtitle={desc}
      icon={icon}
      footer={
        <Link to={to}>
          <Button className="w100">{cta}</Button>
        </Link>
      }
    >
      <div />
    </Card>
  );
}
