"""Career Guidance v2 API — FastAPI + SQLite.

Endpoints:
  GET  /health                     status, keys_configured, llm availability
  POST /auth/register              create account -> JWT
  POST /auth/login                 login -> JWT (demo accounts seeded)
  GET  /users/me                   current user
  GET  /students/profile           my profile
  PUT  /students/profile           save my profile
  GET  /careers                    all careers + required skills + India salary outlook
  POST /assessment/predict         top-3 career predictions with match %
  POST /recommendations            skill gap + courses + projects for a career
  POST /roadmap                    personalised week-by-week roadmap (default 6 weeks)
  POST /study-plan                 daily study plan generator
  POST /chat                       LLM chat: key failover + SQLite cache + KB fallback
  GET  /sessions/{id}/messages     chat history
  GET  /admin/users                admin only: list users
"""
import hashlib
import json
import time

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

from . import chatbot, db
from .config import settings
from .data import CAREER_META, CAREER_SKILLS, FEATURES, FEATURE_LABELS
from .llm import ProviderError, call_with_key, messages_token_count, parse_simulate_failure
from .predictor import engine_name, predict_top_careers
from .recommendation import full_recommendation, generate_roadmap, generate_study_plan
from .security import create_access_token, decode_token, hash_password, verify_password

app = FastAPI(title="AI Career Guidance API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer = HTTPBearer(auto_error=False)

DEMO_USERS = [
    ("Demo Student", "student@college.edu", "student123", "student"),
    ("Demo Admin", "admin@college.edu", "admin123", "admin"),
]


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc.errors())})


def seed_demo_users() -> None:
    for name, email, password, role in DEMO_USERS:
        if db.get_user_by_email(email) is None:
            db.create_user(name, email, hash_password(password), role)


@app.on_event("startup")
def on_startup():
    db.init_db()
    seed_demo_users()


# ------------------------------------------------------------------ auth
def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get_user_by_id(int(payload["user_id"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


def optional_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict | None:
    if creds is None:
        return None
    payload = decode_token(creds.credentials)
    if not payload:
        return None
    return db.get_user_by_id(int(payload["user_id"]))


def public_user(user: dict) -> dict:
    return {"id": user["id"], "name": user["name"], "email": user["email"],
            "role": user["role"], "created_at": user["created_at"]}


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("invalid email")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/register", status_code=201)
def register(payload: RegisterRequest):
    db.init_db()
    user = db.create_user(payload.name.strip(), payload.email, hash_password(payload.password))
    if user is None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    token = create_access_token(user["id"], user["email"], user["role"])
    return {"access_token": token, "token_type": "bearer", "user": public_user(user)}


@app.post("/auth/login")
def login(payload: LoginRequest):
    db.init_db()
    user = db.get_user_by_email(payload.email.strip())
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user["id"], user["email"], user["role"])
    return {"access_token": token, "token_type": "bearer", "user": public_user(user)}


@app.get("/users/me")
def me(user: dict = Depends(current_user)):
    return public_user(user)


@app.get("/admin/users")
def admin_users(user: dict = Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"users": [{k: u[k] for k in ("id", "name", "email", "role", "created_at")}
                      for u in db.list_users()]}


# --------------------------------------------------------------- profile
class ProfileRequest(BaseModel):
    skills: list[str] = []
    interests: str = ""
    education: str = ""
    cgpa: float | None = None
    target_career: str = ""
    hours_per_day: float = 2


@app.get("/students/profile")
def get_my_profile(user: dict = Depends(current_user)):
    return db.get_profile(user["id"])


@app.put("/students/profile")
def save_my_profile(payload: ProfileRequest, user: dict = Depends(current_user)):
    profile = payload.model_dump()
    profile["skills"] = [s.strip() for s in profile["skills"] if s.strip()]
    return db.save_profile(user["id"], profile)


# --------------------------------------------------------------- careers
@app.get("/careers")
def careers():
    out = []
    for career, skills in CAREER_SKILLS.items():
        meta = CAREER_META[career]
        out.append({"career": career, "required_skills": skills, **meta})
    return {"careers": out, "features": FEATURES, "feature_labels": FEATURE_LABELS}


# ------------------------------------------------------------ assessment
class PredictRequest(BaseModel):
    scores: dict[str, float]
    skills: list[str] = []

    @field_validator("scores")
    @classmethod
    def check_scores(cls, v: dict) -> dict:
        cleaned = {}
        for f in FEATURES:
            val = float(v.get(f, 5))
            if not (0 <= val <= 10):
                raise ValueError(f"score for {f} must be between 0 and 10")
            cleaned[f] = val
        return cleaned


@app.post("/assessment/predict")
def predict(payload: PredictRequest, user: dict | None = Depends(optional_user)):
    skills = payload.skills
    if user is not None and not skills:
        skills = db.get_profile(user["id"]).get("skills", [])
    predictions = predict_top_careers(payload.scores, skills, top_n=3)
    enriched = []
    for p in predictions:
        meta = CAREER_META[p["career"]]
        enriched.append({**p, "tagline": meta["tagline"],
                         "salary_range_lpa": [meta["salary_min_lpa"], meta["salary_max_lpa"]],
                         "demand": meta["demand"]})
    if user is not None:
        db.save_assessment(user["id"], payload.scores, predictions)
    return {"predictions": enriched, "engine": engine_name(), "scores": payload.scores}


# --------------------------------------------------------- recommendations
class CareerSkillsRequest(BaseModel):
    career: str
    skills: list[str] = []

    @field_validator("career")
    @classmethod
    def check_career(cls, v: str) -> str:
        if v not in CAREER_SKILLS:
            raise ValueError(f"unknown career; choose one of {sorted(CAREER_SKILLS)}")
        return v


@app.post("/recommendations")
def recommendations(payload: CareerSkillsRequest, user: dict | None = Depends(optional_user)):
    skills = payload.skills
    if user is not None and not skills:
        skills = db.get_profile(user["id"]).get("skills", [])
    result = full_recommendation(skills, payload.career)
    result["meta"] = CAREER_META[payload.career]
    return result


class RoadmapRequest(CareerSkillsRequest):
    weeks: int = Field(default=6, ge=2, le=12)


@app.post("/roadmap")
def roadmap(payload: RoadmapRequest, user: dict | None = Depends(optional_user)):
    skills = payload.skills
    if user is not None and not skills:
        skills = db.get_profile(user["id"]).get("skills", [])
    return generate_roadmap(payload.career, skills, payload.weeks)


class StudyPlanRequest(RoadmapRequest):
    hours_per_day: float = Field(default=2, gt=0, le=12)
    days_per_week: int = Field(default=6, ge=1, le=7)


@app.post("/study-plan")
def study_plan(payload: StudyPlanRequest, user: dict | None = Depends(optional_user)):
    skills = payload.skills
    if user is not None and not skills:
        profile = db.get_profile(user["id"])
        skills = profile.get("skills", [])
    return generate_study_plan(payload.career, skills, payload.hours_per_day,
                               payload.days_per_week, payload.weeks)


# ---------------------------------------------------------------- health
@app.get("/health")
def health():
    db.init_db()
    conn = db.get_conn()
    try:
        conn.execute("SELECT 1").fetchone()
    finally:
        conn.close()
    return {
        "status": "ok",
        "version": "2.0.0",
        "keys_configured": settings.keys_configured,
        "llm_available": settings.llm_available,
        "model": settings.llm_model,
        "cache_enabled": settings.cache_enabled,
        "prediction_engine": engine_name(),
    }


# ------------------------------------------------------------------ chat
class ChatRequest(BaseModel):
    session_id: str
    message: str

    @field_validator("session_id")
    @classmethod
    def check_session(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 128):
            raise ValueError("session_id must be 1-128 chars")
        return v

    @field_validator("message")
    @classmethod
    def check_message(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 4000):
            raise ValueError("message must be 1-4000 chars after trimming")
        return v


@app.post("/chat")
async def chat(payload: ChatRequest,
               user: dict | None = Depends(optional_user),
               x_simulate_failure: str | None = Header(default=None)):
    start = time.perf_counter()
    db.init_db()
    db.ensure_chat_session(payload.session_id, user["id"] if user else None)

    profile = db.get_profile(user["id"]) if user else {}
    predictions = None
    if user:
        latest = db.latest_assessment(user["id"])
        if latest:
            predictions = latest["predictions"]

    history = [{"role": m["role"], "content": m["content"]}
               for m in db.get_chat_messages(payload.session_id)]
    system_prompt = chatbot.build_system_prompt(profile, predictions)
    kb_context = chatbot.knowledge_context(payload.message)
    if kb_context:
        system_prompt += "\n" + kb_context
    full_messages = ([{"role": "system", "content": system_prompt}] + history
                     + [{"role": "user", "content": payload.message}])

    # --- Cache lookup (model + full message list), Lyftr pattern ---------
    cache_key = hashlib.sha256(
        json.dumps({"model": settings.llm_model, "messages": full_messages}, sort_keys=True).encode()
    ).hexdigest()
    cached = db.cache_get(cache_key) if settings.cache_enabled else None
    if cached is not None:
        latency_ms = max(1, int((time.perf_counter() - start) * 1000))
        metadata = {"resolution_source": "LLM_CACHE", "model": cached["model"],
                    "latency_ms": latency_ms, "input_tokens": cached["input_tokens"],
                    "output_tokens": cached["output_tokens"], "key_id": None,
                    "fallback_attempts": 0}
        db.add_chat_message(payload.session_id, "user", payload.message)
        db.add_chat_message(payload.session_id, "assistant", cached["reply"], metadata)
        return {"session_id": payload.session_id, "reply": cached["reply"], "metadata": metadata}

    # --- Live inference with key failover --------------------------------
    simulate = parse_simulate_failure(x_simulate_failure) if settings.enable_failure_simulation else {}
    keys = settings.real_keys
    fallback_attempts = 0
    result = None
    result_key_id = None

    for idx, key in enumerate(keys):
        key_id = f"key_{idx + 1}"
        simulated_status = simulate.get(key_id, simulate.get("*"))
        if simulated_status is not None:
            fallback_attempts += 1
            continue
        try:
            result = await call_with_key(key, full_messages)
            result_key_id = key_id
            break
        except ProviderError:
            fallback_attempts += 1
            result = None

    if result is not None:
        reply, input_tokens, output_tokens = result
        latency_ms = int((time.perf_counter() - start) * 1000)
        metadata = {"resolution_source": "LIVE_INFERENCE", "model": settings.llm_model,
                    "latency_ms": latency_ms, "input_tokens": input_tokens,
                    "output_tokens": output_tokens, "key_id": result_key_id,
                    "fallback_attempts": fallback_attempts}
        if settings.cache_enabled:
            db.cache_put(cache_key, reply, settings.llm_model, input_tokens, output_tokens)
        db.add_chat_message(payload.session_id, "user", payload.message)
        db.add_chat_message(payload.session_id, "assistant", reply, metadata)
        return {"session_id": payload.session_id, "reply": reply, "metadata": metadata}

    # --- Graceful fallback: built-in knowledge base (site always works) --
    fb = chatbot.fallback_answer(payload.message, profile, predictions)
    latency_ms = int((time.perf_counter() - start) * 1000)
    metadata = {"resolution_source": "FALLBACK_KB", "model": "knowledge-base",
                "latency_ms": latency_ms,
                "input_tokens": messages_token_count(full_messages),
                "output_tokens": messages_token_count([{"content": fb["answer"]}]),
                "key_id": None, "fallback_attempts": fallback_attempts,
                "sources": fb["sources"]}
    if settings.cache_enabled:
        db.cache_put(cache_key, fb["answer"], "knowledge-base",
                     metadata["input_tokens"], metadata["output_tokens"])
    db.add_chat_message(payload.session_id, "user", payload.message)
    db.add_chat_message(payload.session_id, "assistant", fb["answer"], metadata)
    return {"session_id": payload.session_id, "reply": fb["answer"], "metadata": metadata}


@app.get("/sessions/{session_id}/messages")
def session_messages(session_id: str):
    db.init_db()
    if not db.chat_session_exists(session_id):
        raise HTTPException(status_code=404, detail="session not found")
    return {"session_id": session_id, "messages": db.get_chat_messages(session_id)}
