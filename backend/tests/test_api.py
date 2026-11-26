"""End-to-end API tests for Career Guidance v2.

Runs against a throwaway SQLite DB with NO LLM keys configured, so the
chat tests exercise the knowledge-base fallback path and the cache.
"""
import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["LLM_API_KEYS"] = ""
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Enter the TestClient context so FastAPI startup events run
# (DB init + demo-user seeding).
_client_ctx = TestClient(app)
client = _client_ctx.__enter__()

SCORES_DS = {"math": 9, "logical_reasoning": 8, "creativity": 6, "communication": 7,
             "programming": 8, "data_interest": 10, "design_interest": 4, "business_interest": 6}
SCORES_UX = {"math": 3, "logical_reasoning": 6, "creativity": 10, "communication": 8,
             "programming": 4, "data_interest": 3, "design_interest": 10, "business_interest": 6}


def _auth_headers():
    r = client.post("/auth/login", json={"email": "student@college.edu", "password": "student123"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# ---------------------------------------------------------------- health
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["keys_configured"] == 0
    assert body["llm_available"] is False
    assert body["cache_enabled"] is True


# ------------------------------------------------------------------ auth
def test_demo_student_login():
    r = client.post("/auth/login", json={"email": "student@college.edu", "password": "student123"})
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "student"
    assert r.json()["access_token"]


def test_demo_admin_login_and_admin_endpoint():
    r = client.post("/auth/login", json={"email": "admin@college.edu", "password": "admin123"})
    assert r.status_code == 200
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    users = client.get("/admin/users", headers=headers)
    assert users.status_code == 200
    assert len(users.json()["users"]) >= 2


def test_admin_endpoint_forbidden_for_student():
    r = client.get("/admin/users", headers=_auth_headers())
    assert r.status_code == 403


def test_login_wrong_password():
    r = client.post("/auth/login", json={"email": "student@college.edu", "password": "wrong"})
    assert r.status_code == 401


def test_register_and_me():
    r = client.post("/auth/register",
                    json={"name": "Test User", "email": "test.user@example.com", "password": "secret123"})
    assert r.status_code == 201
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "test.user@example.com"


def test_register_duplicate_email():
    client.post("/auth/register",
                json={"name": "Dup One", "email": "dup@example.com", "password": "secret123"})
    r = client.post("/auth/register",
                    json={"name": "Dup Two", "email": "dup@example.com", "password": "secret123"})
    assert r.status_code == 409


def test_me_requires_auth():
    assert client.get("/users/me").status_code == 401


# --------------------------------------------------------------- profile
def test_profile_save_and_get():
    headers = _auth_headers()
    payload = {"skills": ["Python", "SQL"], "interests": "data, charts",
               "education": "MCA", "cgpa": 8.4, "target_career": "Data Scientist",
               "hours_per_day": 3}
    r = client.put("/students/profile", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["skills"] == ["Python", "SQL"]
    got = client.get("/students/profile", headers=headers)
    assert got.status_code == 200
    assert got.json()["target_career"] == "Data Scientist"


# -------------------------------------------------------------- careers
def test_careers_list():
    r = client.get("/careers")
    assert r.status_code == 200
    careers = r.json()["careers"]
    assert len(careers) == 8
    ml = [c for c in careers if c["career"] == "ML Engineer"][0]
    assert "Python" in ml["required_skills"]
    assert ml["salary_max_lpa"] > ml["salary_min_lpa"]


# -------------------------------------------------------------- predict
def test_predict_top3_for_data_profile():
    r = client.post("/assessment/predict", json={"scores": SCORES_DS, "skills": ["Python"]})
    assert r.status_code == 200
    preds = r.json()["predictions"]
    assert len(preds) == 3
    assert preds[0]["career"] in {"Data Scientist", "ML Engineer", "AI Researcher", "Data Analyst"}
    assert preds[0]["match_pct"] >= preds[1]["match_pct"] >= preds[2]["match_pct"]
    assert all(0 < p["match_pct"] <= 100 for p in preds)


def test_predict_top3_for_design_profile():
    r = client.post("/assessment/predict", json={"scores": SCORES_UX, "skills": []})
    assert r.status_code == 200
    assert r.json()["predictions"][0]["career"] == "UI/UX Designer"


def test_predict_rejects_out_of_range_score():
    bad = dict(SCORES_DS, math=42)
    r = client.post("/assessment/predict", json={"scores": bad, "skills": []})
    assert r.status_code == 422


def test_predict_saves_assessment_for_logged_in_user():
    headers = _auth_headers()
    r = client.post("/assessment/predict", json={"scores": SCORES_DS, "skills": []}, headers=headers)
    assert r.status_code == 200


# -------------------------------------------------------- recommendations
def test_recommendations_skill_gap():
    r = client.post("/recommendations",
                    json={"career": "Data Scientist", "skills": ["Python", "SQL"]})
    assert r.status_code == 200
    body = r.json()
    assert body["matched"] == ["Python", "SQL"]
    assert "Statistics" in body["gaps"]
    assert 0 < body["coverage_pct"] < 100
    assert body["courses"], "expected course recommendations for gap skills"
    assert body["projects"]


def test_recommendations_unknown_career():
    r = client.post("/recommendations", json={"career": "Wizard", "skills": []})
    assert r.status_code == 422


# --------------------------------------------------------------- roadmap
def test_roadmap_six_weeks():
    r = client.post("/roadmap",
                    json={"career": "ML Engineer", "skills": ["Python"], "weeks": 6})
    assert r.status_code == 200
    body = r.json()
    assert body["weeks"] == 6
    assert len(body["plan"]) == 6
    assert [w["week"] for w in body["plan"]] == [1, 2, 3, 4, 5, 6]
    assert body["plan"][-1]["title"].startswith("Portfolio project")
    all_focus = [s for w in body["plan"] for s in w["focus_skills"]]
    assert "Machine Learning" in all_focus


def test_roadmap_uses_profile_skills_when_logged_in():
    headers = _auth_headers()  # profile saved earlier has Python + SQL
    r = client.post("/roadmap", json={"career": "Data Analyst", "weeks": 6}, headers=headers)
    assert r.status_code == 200
    assert "Python" in r.json()["matched"]


# ------------------------------------------------------------ study plan
def test_study_plan():
    r = client.post("/study-plan",
                    json={"career": "Full-Stack Developer", "skills": ["HTML/CSS"],
                          "hours_per_day": 2, "days_per_week": 5, "weeks": 6})
    assert r.status_code == 200
    body = r.json()
    assert body["total_hours"] == 60.0
    assert len(body["schedule"]) == 6
    assert body["daily_routine"][0]["minutes_per_day"] == 60


# ------------------------------------------------------------------ chat
def test_chat_fallback_answers_and_history():
    payload = {"session_id": "s-fallback", "message": "What is the roadmap for a Data Scientist?"}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["reply"]
    assert body["metadata"]["resolution_source"] == "FALLBACK_KB"

    hist = client.get("/sessions/s-fallback/messages")
    assert hist.status_code == 200
    msgs = hist.json()["messages"]
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_chat_cache_hit_on_repeat():
    # The cache key is model + full message list, so an identical request in
    # an identical conversation state (fresh session, same first message)
    # must be served from the cache with the identical reply.
    msg = "Tell me about fresher salaries in India"
    first = client.post("/chat", json={"session_id": "s-cache-a", "message": msg})
    assert first.status_code == 200
    second = client.post("/chat", json={"session_id": "s-cache-b", "message": msg})
    assert second.status_code == 200
    assert second.json()["reply"] == first.json()["reply"]
    assert second.json()["metadata"]["resolution_source"] == "LLM_CACHE"


def test_chat_simulated_failure_still_falls_back():
    payload = {"session_id": "s-simfail", "message": "How does the AI in this system work?"}
    r = client.post("/chat", json=payload, headers={"X-Simulate-Failure": "*=503"})
    assert r.status_code == 200
    assert r.json()["metadata"]["resolution_source"] in {"FALLBACK_KB", "LLM_CACHE"}


def test_chat_unknown_session_404():
    assert client.get("/sessions/does-not-exist/messages").status_code == 404


def test_chat_validation():
    r = client.post("/chat", json={"session_id": "s-x", "message": "   "})
    assert r.status_code == 422
