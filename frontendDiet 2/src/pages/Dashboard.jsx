import { useNavigate } from "react-router-dom";
import "../styles/globals.css";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="dashboard-wrapper">
      <h1 className="dashboard-title">App Features</h1>

      <div className="features-grid">
        <FeatureCard
          icon="📝"
          title="Log Your Meals"
          description="Record your breakfast, lunch, and dinner"
          buttonText="Log Meals"
          onClick={() => navigate("/meals")}
        />

        <FeatureCard
          icon="🔥"
          title="Track Calories"
          description="Monitor how many calories you consume"
          buttonText="Dashboard"
          onClick={() => navigate("/dashboard")}
        />

        <FeatureCard
          icon="🥗"
          title="Macros Breakdown"
          description="Coming soon"
          buttonText="Soon"
          onClick={() => {}}
        />

        <FeatureCard
          icon="🎯"
          title="Set Goals"
          description="Coming soon"
          buttonText="Soon"
          onClick={() => {}}
        />
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description, buttonText, onClick }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <button className="feature-btn" onClick={onClick}>
        {buttonText}
      </button>
    </div>
  );
}