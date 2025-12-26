# Diet AI Frontend (React + Vite)

Minimal blue/white frontend that matches your reference style and surfaces the *user-facing* parts of your backend:

- Profile (drives personalization)
- Calorie + macro targets
- AI meal plan (generate / swap / regenerate)
- Grocery list
- Stores map (nearby stores from backend)

## 1) Setup

```bash
cd diet-frontend
npm install
cp .env.example .env
```

Edit `.env` if your backend isn't running on `http://localhost:8000`.

## 2) Run

```bash
npm run dev
```

## Backend expectations

Your backend must enable CORS (it does in `main.py`) and run on the URL in `VITE_API_BASE_URL`.

Notes:
- Store map uses OpenStreetMap tiles + Leaflet in the frontend.
- The backend `/stores` endpoint still uses Google Places (needs `GOOGLE_MAPS_API_KEY` on the backend).
