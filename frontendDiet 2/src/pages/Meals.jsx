import { useState } from "react";
import "./Meals.css";

export default function Meals() {
  const [date, setDate] = useState(new Date());

  const meals = [
    { key: "breakfast", label: "Breakfast", icon: "🍳" },
    { key: "lunch", label: "Lunch", icon: "🥪" },
    { key: "dinner", label: "Dinner", icon: "🍽️" },
  ];

  return (
    <div className="meals-container">
      <h1 className="meals-title">Log Meals</h1>

      <DateSelector date={date} setDate={setDate} />

      <div className="meals-list">
        {meals.map((meal) => (
          <MealCard key={meal.key} meal={meal} />
        ))}
      </div>

      <button className="quick-add-btn">+ Quick Add</button>
    </div>
  );
}

function DateSelector({ date, setDate }) {
  const formatDate = (d) =>
    d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });

  return (
    <div className="date-selector">
      <button onClick={() => setDate(new Date(date.setDate(date.getDate() - 1)))}>
        ‹
      </button>
      <span>Today – {formatDate(date)}</span>
      <button onClick={() => setDate(new Date(date.setDate(date.getDate() + 1)))}>
        ›
      </button>
    </div>
  );
}
import MealPlanGrid from "./MealPlanGrid";

function Meals() {
  return (
    <>
      {/* Existing meal logging UI */}
      <MealPlanGrid />
    </>
  );
}