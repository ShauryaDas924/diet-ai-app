export default function MealCard({ meal }) {
  return (
    <div className="meal-card">
      {meal.icon} {meal.label}
    </div>
  );
}