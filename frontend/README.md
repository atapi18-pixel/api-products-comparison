Local frontend setup

1. Install dependencies

cd frontend
npm install

2. Run dev server (uses VITE_API_BASE from .env)

npm run dev

3. Build for production

npm run build

Notes:
- Ensure the backend is running at the URL configured in `frontend/.env` (default: http://localhost:8000)
- If you see stale assets, remove `frontend/dist` and rebuild.
