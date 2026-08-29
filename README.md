# EvoPay AI

EvoPay AI is a hackathon prototype foundation for a self-evolving payment fraud defense platform. Future iterations will pair a simulated Red Team, which generates fraudulent payment attacks, with a Blue Team, which detects and mitigates them.

This phase includes a polished landing screen, a `/dashboard` placeholder, a FastAPI health endpoint, CORS configuration, and a SQLite-ready database layer.

## Frontend

Requirements: Node.js 18+ and npm.

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Select **Enter Security Lab** to navigate to `http://localhost:5173/dashboard`.

To create a production build:

```powershell
npm run build
```

## Backend

Requirements: Python 3.10+.

Open another terminal:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

Test the health endpoint in PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok","service":"evopay-ai"}
```

CORS allows the local Vite origins `http://localhost:5173` and `http://127.0.0.1:5173`.

## API surface

The backend seeds synthetic SQLite data on first startup and exposes:

```text
GET  /api/health
GET  /api/dashboard
GET  /api/transactions
GET  /api/transactions/{transaction_id}
POST /api/transactions/{transaction_id}/action
GET  /api/attacks
POST /api/attacks/generate
POST /api/attacks/evolve
GET  /api/network
POST /api/simulation/start
GET  /api/simulation/{simulation_id}
GET  /api/incidents
GET  /api/analytics
GET  /api/threat-library
POST /api/threat-library
POST /api/investigate
```

The frontend uses `http://127.0.0.1:8000/api` by default. Set `VITE_API_URL` when the API runs elsewhere. If the API is unavailable, the dashboard keeps its local synthetic fallback data.
