import "./MealPlanGrid.css";

const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const meals = [
  { key: "breakfast", label: "Breakfast", icon: "🍳" },
  { key: "lunch", label: "Lunch", icon: "🥪" },
  { key: "dinner", label: "Dinner", icon: "🍽️" },
  { key: "snack", label: "Snack", icon: "🍎" },
];

export default function MealPlanGrid() {
  return (
    <div className="mealplan-container">
      <h2 className="mealplan-title">Meal Plan</h2>

      <div className="mealplan-grid">
        {/* Header Row */}
        <div className="corner-cell"></div>
        {days.map((day) => (
          <div key={day} className="header-cell">
            {day}
          </div>
        ))}

        {/* Meal Rows */}
        {meals.map((meal) => (
          <MealRow key={meal.key} meal={meal} />
        ))}
      </div>
    </div>
  );
}
function MealRow({ meal }) {
  return (
    <>
      <div className="meal-label">{meal.label}</div>

      {Array.from({ length: 7 }).map((_, idx) => (
        <div key={idx} className="meal-cell">
          <span className="meal-icon">{meal.icon}</span>
        </div>
      ))}

      {/* View Macros Button Row */}
      <div className="view-macros-label"></div>
      {Array.from({ length: 7 }).map((_, idx) => (
        <div key={idx} className="macros-cell">
          <button className="macros-btn">View Macros</button>
        </div>
      ))}
    </>
  );
}