# Run in VS Code (laptop guide)

Same one-click flow as the Lyftr assignment project.

## First time only

1. Open this folder (`career-guidance-v2`) in VS Code.
2. Press **Ctrl+Shift+P → Tasks: Run Task → "Install ALL (backend + frontend)"** and wait for it to finish.
3. (Optional, for live AI chat) Copy `backend/.env.example` to `backend/.env` and paste your
   Gemini keys into `LLM_API_KEYS` (comma-separated). Without keys the chat still works —
   it answers from the built-in knowledge base.

## Every time you want to run the website

1. **Tasks: Run Task → "Run Backend (FastAPI :8000)"** — wait for `Application startup complete`.
   Check it: open http://localhost:8000/health in the browser.
2. **Tasks: Run Task → "Run Frontend (Vite :5173)"**.
3. Open **http://localhost:5173** in Chrome.
4. Log in with the demo account: `student@college.edu` / `student123`
   (admin: `admin@college.edu` / `upes123`), or register your own account.

## Other tasks

- **"Run Backend Tests (pytest)"** — runs the full API test suite (24 tests).
- **"Build Frontend (production)"** — creates `frontend/dist` for deployment.

## Manual fallback (no VS Code tasks)

```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

## Debugging

Use the **Run and Debug** panel: "Debug Backend (FastAPI)" starts the API under the
debugger; "Open Frontend (Chrome)" opens the site in Chrome with debugging attached.
