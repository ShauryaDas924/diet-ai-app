function MealCard({ meal }) {
  return (
    <div className="meal-card">
      <div className="meal-left">
        <span className="meal-icon">{meal.icon}</span>
        <div>
          <h3>{meal.label}</h3>
          <p>No items logged</p>
        </div>
      </div>

      <button className="add-food-btn">+ Add Food</button>
    </div>
  );
}