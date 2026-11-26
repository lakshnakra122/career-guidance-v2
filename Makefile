.PHONY: backend frontend test build install

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && python -m pytest -q

build:
	cd frontend && npm run build
