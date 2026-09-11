# Navjeevan AI

Navjeevan AI is an agriculture decision-support platform for Gujarat farmers. It combines market and mandi information, weather and spray-risk guidance, government scheme and document assistance, trader contacts, and an agricultural chat assistant.

## Current Architecture

```text
Vercel
  React + Vite frontend (frontend/, output: dist)
             |
             v
Render Web Service
  FastAPI backend (backend.main:app)
             |
             +-- Groq (optional intent and response formatting)
             +-- Open-Meteo / OpenWeatherMap (weather)
             +-- data.gov.in Agmarknet resource (optional live mandi prices)
```

React/Vite is the only production frontend. The backend is not deployed to Vercel.

## Local Setup

### Backend

Requirements: Python 3.10+.

```powershell
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The backend runs at `http://127.0.0.1:8000`.

### Frontend

Requirements: Node.js 18+ and npm.

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

The Vite development server proxies `/chat`, `/api`, and `/health` to the local backend. The production API URL is configured with `VITE_API_BASE_URL`.

## Environment Variables

Backend variables are documented in [.env.example](.env.example). Frontend variables are documented in [frontend/.env.example](frontend/.env.example).

Never commit `.env`, `.env.local`, API keys, or other secrets.

Important backend variables:

- `GROQ_API_KEY`: optional Groq key for AI intent parsing and response formatting.
- `DATA_GOV_API_KEY`: optional data.gov.in key for live Agmarknet mandi prices.
- `OPENWEATHER_API_KEY`: optional OpenWeatherMap key; Open-Meteo remains the fallback provider.
- `FRONTEND_ORIGINS`: comma-separated allowed browser origins, including the deployed Vercel URL.
- `ENVIRONMENT`: use `production` on Render to require explicitly configured CORS origins.
- `GROQ_MODEL`, `GROQ_TIMEOUT_SECONDS`, `EXTERNAL_API_TIMEOUT_SECONDS`: optional runtime settings.
- `RATE_LIMIT_WINDOW_SECONDS`, `CHAT_RATE_LIMIT_REQUESTS`, `EXTERNAL_API_RATE_LIMIT_REQUESTS`: in-memory public API protection settings.

When `DATA_GOV_API_KEY` is absent or the live request fails, market responses explicitly identify the cached result as `Cached / Historical Data` and include its arrival date.

## API Endpoints

- `GET /health`: public backend health check. It returns only `{"status":"ok"}` and exposes no keys, filesystem paths, or diagnostic details.
- `GET /`: canonical React production HTML, served only when `frontend/dist` exists.
- `POST /chat`: agricultural intent routing and response generation.
- `GET /api/v1/weather?location=Surat`: current weather and three-day rainfall forecast.
- `POST /api/v1/advisory`: rule-based crop advisory with optional AI formatting.

The API returns JSON response envelopes for `/chat`, `/api/v1/weather`, and `/api/v1/advisory`. `/health` returns a small health JSON object; `/` returns HTML and is not a health check.

### Health Monitoring

Use `GET /health` to confirm that the FastAPI backend is running. Configure this endpoint as the Render health check and monitor it with UptimeRobot if desired.

Production URL format:

```text
https://YOUR-RENDER-URL/health
```

Expected response:

```json
{"status":"ok"}
```

## Vercel Deployment

Create a Vercel project with:

- Root Directory: `frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm ci`
- Environment Variable: `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`

The same settings are captured in [frontend/vercel.json](frontend/vercel.json). Do not add backend secrets to Vercel.

## Render Deployment

Create an always-on Render Web Service from the repository:

- Runtime: Python
- Root Directory: repository root
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

Set the backend variables from `.env.example` in the Render dashboard. Set `FRONTEND_ORIGINS` to the Vercel deployment origin, for example `https://your-app.vercel.app`, and include local origins only when needed.

Render uses an always-on Web Service. Chat, weather, and advisory/external operations have configurable per-client in-memory rate limits; use a shared rate-limit service before scaling to multiple backend instances.

The equivalent configuration is in [render.yaml](render.yaml). No container deployment is required.

## Testing

From the repository root:

```powershell
python -m compileall -q backend
python -m pytest backend/tests -q
```

Build the frontend:

```powershell
cd frontend
npm ci
npm run build
```

The frontend package currently has no lint script. Add a project-approved lint tool before making lint a CI deployment gate.
