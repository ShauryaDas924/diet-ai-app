import { useNavigate } from "react-router-dom";
import "../styles/globals.css"

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-wrapper">
      <h1 className="home-title">Diet Tracker App</h1>

      <img
        src={foodIllustration}
        alt="Healthy food illustration"
        className="home-image"
      />

      <p className="home-subtitle">
        Track your daily calories and <br />
        log meals to achieve your diet goals
      </p>

      <button
        className="get-started-btn"
        onClick={() => navigate("/")}
      >
        Get Started
      </button>
    </div>
  );
}