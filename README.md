# PathFinder AI — AI-Powered Personalized Learning & Career Recommendation System (v2)

A complete rebuild of the minor project with a modern UI and a real LLM-powered
mentor chat. A student takes an 8-dimension assessment, an ML model predicts their
**top-3 careers with match %**, the engine maps their **skill gaps**, recommends
**courses & projects**, and generates a **personalised 6-week roadmap** and a
**daily study plan**. The **AI Mentor Chat** runs on a real LLM (LiteLLM + Gemini)
with multi-key failover and response caching — and falls back to a built-in
knowledge base so it always answers.

> **Live URLs:** Frontend: `<FRONTEND_URL>` · Backend: `<BACKEND_URL>` (fill in after deployment)
> **Demo accounts:** `student@college.edu` / `student123` · `admin@college.edu` / `upes123`

## Features

- **Auth** — JWT register/login, seeded demo student + admin accounts, admin user list.
- **Profile** — skills, interests, education, CGPA, target career, study hours.
- **Assessment → Prediction** — K-Nearest Neighbors (KNN) (trained in memory at startup; profile-similarity
  fallback) over 8 features, blended with skill overlap → calibrated top-3 match %.
- **Skill-Gap Analysis** — coverage %, matched vs missing skills, a course for every gap, project ideas.
- **Roadmap** — week-by-week plan (default 6 weeks): gap skills sequenced foundations-first,
  tasks, courses and a checkpoint per week, portfolio project in the final week.
- **Study Plan Generator** — daily Learn/Practice/Build routine sized to your hours/day.
- **AI Mentor Chat** — LiteLLM chat with the student's profile + assessment as context,
  key failover (`key_1`, `key_2`, …), SQLite response cache (`LLM_CACHE` vs `LIVE_INFERENCE`),
  `X-Simulate-Failure` test hook, and a knowledge-base fallback (`FALLBACK_KB`) when no
  keys are configured or all providers fail.
- **Careers catalogue** — 8 careers with required skills, demand and India fresher salary outlook.

## Architecture

```
frontend/ (React + Vite)                backend/ (FastAPI + SQLite)
  Landing / Login / Register              app/main.py        API routes
  Dashboard (sidebar layout)              app/predictor.py   ML prediction (RF + similarity)
  Assessment · Careers · Skill Gap        app/recommendation.py  gap / roadmap / study plan
  Roadmap · Study Plan · Chat · Profile   app/chatbot.py     context + KB retrieval/fallback
        │  REST + JWT                     app/llm.py         LiteLLM failover client
        └──────────────►                  app/db.py          users, profiles, chat, llm_cache
                                          app/data.py        careers, courses, projects, KB
```

## Quick start (laptop)

See **RUN_IN_VSCODE.md** for the one-click VS Code flow. Manual:

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000        # http://localhost:8000/health

# Frontend
cd frontend && npm install
npm run dev                                       # http://localhost:5173
```

Or everything in Docker: `docker compose up --build` → frontend on :5173, backend on :8000.

## Environment variables (backend)

| Variable | Default | Purpose |
|---|---|---|
| `LLM_API_KEYS` | *(empty)* | Comma-separated provider keys for chat failover. Empty = offline KB mode. |
| `LLM_MODEL` | `gemini/gemini-3.5-flash-lite` | LiteLLM model id |
| `DATABASE_URL` | `sqlite:///./career_guidance.db` | SQLite location |
| `ALLOWED_ORIGINS` | localhost:5173,3000 | CORS origins (set to the frontend URL in production) |
| `JWT_SECRET` | dev placeholder | **Change in production** |
| `JWT_EXPIRE_MINUTES` | `1440` | Token lifetime |
| `ENABLE_FAILURE_SIMULATION` | `true` | Enables the `X-Simulate-Failure` chat header |

Frontend: `VITE_API_URL` = backend base URL (no trailing slash).

## Tests

```bash
cd backend && python -m pytest -q   # 24 tests: health, auth, profile, predict,
                                    # recommendations, roadmap, study plan, chat fallback + cache
```

## Deploy the backend (Render)

1. Push this repo to GitHub.
2. Render → **New → Blueprint** → select the repo (uses `render.yaml`, Docker, `backend/Dockerfile`).
3. In the service's Environment tab set **`LLM_API_KEYS`** (your Gemini keys, comma-separated)
   and **`ALLOWED_ORIGINS`** (your frontend URL). `JWT_SECRET` is auto-generated.
4. Verify: `https://<your-backend>.onrender.com/health` → `"status": "ok"`.

## Deploy the frontend (Netlify or Render Static)

- **Netlify:** New site from the repo → base directory `frontend`, build command `npm run build`,
  publish directory `dist`, environment variable `VITE_API_URL=https://<your-backend>.onrender.com`.
  Make the site **Public** (Site configuration → Visibility) so anyone can open it.
- **Render Static Site:** root directory `frontend`, build `npm install && npm run build`,
  publish `dist`, same `VITE_API_URL` env var, plus a rewrite rule `/* → /index.html`.

## Project layout

```
career-guidance-v2/
├── backend/            FastAPI app, tests, Dockerfile, .env.example
├── frontend/           React + Vite app, Dockerfile (nginx), .env.example
├── render.yaml         Render Blueprint for the backend
├── docker-compose.yml  Full local stack
├── Makefile            install / backend / frontend / test / build
├── RUN_IN_VSCODE.md    One-click laptop run guide
└── .vscode/            Tasks + debug configs
```
