import { useState, useEffect } from 'react';

export default function Nutrition() {
    const [nutrition, setNutrition] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchNutrition = async () => {
            try {
                const response = await fetch('/api/nutrition');
                if (!response.ok) throw new Error('Failed to fetch nutrition data');
                const data = await response.json();
                setNutrition(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchNutrition();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="nutrition-container">
            <h1>Nutrition Information</h1>
            {nutrition && (
                <div className="nutrition-details">
                    <p><strong>Calories:</strong> {nutrition.calories}</p>
                    <p><strong>Protein:</strong> {nutrition.protein}g</p>
                    <p><strong>Carbs:</strong> {nutrition.carbs}g</p>
                    <p><strong>Fat:</strong> {nutrition.fat}g</p>
                </div>
            )}
        </div>
    );
}