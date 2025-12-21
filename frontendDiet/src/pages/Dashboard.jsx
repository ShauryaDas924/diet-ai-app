import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

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
          buttonText="View Calories"
          onClick={() => navigate("/home")}
        />

        <FeatureCard
          icon="🥗"
          title="Macros Breakdown"
          description="See the carbs, protein, and fat you eat"
          buttonText="View Macros"
          onClick={() => navigate("/nutrition")}
        />

        <FeatureCard
          icon="🎯"
          title="Set Goals"
          description="Define calorie and nutrient targets"
          buttonText="Set Goals"
          onClick={() => navigate("/profile")}
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