import React, { useState } from 'react';

export default function Meals() {
const [meals, setMeals] = useState([]);

const [mealInput, setMealInput] = useState('');

const addMeal = () => {
    if (mealInput.trim()) {
        setMeals([...meals, { id: Date.now(), text: mealInput }]);
        setMealInput('');
    }
};

    return (
        <div className="meals-container">
            <h1>Meals</h1>
            <p>Welcome to the Meals page</p>
            
            <div className="meal-input-section">
                <input
                    type="text"
                    value={mealInput}
                    onChange={(e) => setMealInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addMeal()}
                    placeholder="Enter your meal"
                />
                <button onClick={addMeal}>Add Meal</button>
            </div>

            <ul className="meals-list">
                {meals.map((meal) => (
                    <li key={meal.id}>{meal.text}</li>
                ))}
            </ul>

            <div className="date-display">
                <p>Date: {new Date().toLocaleDateString()}</p>
            </div>
            </ul>
        </div>
    );
}