"""SQLite storage for Career Guidance v2.

One database file holds everything: user accounts, student profiles,
saved assessments, chat sessions/messages and the LLM response cache
(same cache design as the Lyftr assignment).
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

from .config import settings


def db_path_from_url(url: str) -> str:
    if url.startswith("sqlite:////"):
        return "/" + url[len("sqlite:////"):]
    if url.startswith("sqlite:///"):
        return url[len("sqlite:///"):]
    if url.startswith("sqlite://"):
        return url[len("sqlite://"):]
    return url


DB_PATH = db_path_from_url(settings.database_url)


def get_conn() -> sqlite3.Connection:
    directory = os.path.dirname(os.path.abspath(DB_PATH))
    if directory:
        os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id),
                skills TEXT NOT NULL DEFAULT '[]',
                interests TEXT NOT NULL DEFAULT '',
                education TEXT NOT NULL DEFAULT '',
                cgpa REAL,
                target_career TEXT NOT NULL DEFAULT '',
                hours_per_day REAL NOT NULL DEFAULT 2,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scores TEXT NOT NULL,
                predictions TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id, id);
            CREATE TABLE IF NOT EXISTS llm_cache (
                cache_key TEXT PRIMARY KEY,
                reply TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------- users
def create_user(name: str, email: str, password_hash: str, role: str = "student") -> dict | None:
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email.lower(), password_hash, role, now_iso()),
        )
        conn.commit()
        return get_user_by_id(cur.lastrowid)
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_users() -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute("SELECT id, name, email, role, created_at FROM users ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ------------------------------------------------------------- profiles
def save_profile(user_id: int, profile: dict) -> dict:
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO profiles (user_id, skills, interests, education, cgpa, target_career, hours_per_day, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                 skills=excluded.skills, interests=excluded.interests, education=excluded.education,
                 cgpa=excluded.cgpa, target_career=excluded.target_career,
                 hours_per_day=excluded.hours_per_day, updated_at=excluded.updated_at""",
            (user_id, json.dumps(profile.get("skills", [])), profile.get("interests", ""),
             profile.get("education", ""), profile.get("cgpa"), profile.get("target_career", ""),
             profile.get("hours_per_day", 2), now_iso()),
        )
        conn.commit()
    finally:
        conn.close()
    return get_profile(user_id)


def get_profile(user_id: int) -> dict:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            return {"user_id": user_id, "skills": [], "interests": "", "education": "",
                    "cgpa": None, "target_career": "", "hours_per_day": 2}
        d = dict(row)
        d["skills"] = json.loads(d["skills"] or "[]")
        return d
    finally:
        conn.close()


# ---------------------------------------------------------- assessments
def save_assessment(user_id: int | None, scores: dict, predictions: list) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO assessments (user_id, scores, predictions, created_at) VALUES (?, ?, ?, ?)",
            (user_id, json.dumps(scores), json.dumps(predictions), now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def latest_assessment(user_id: int) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["scores"] = json.loads(d["scores"])
        d["predictions"] = json.loads(d["predictions"])
        return d
    finally:
        conn.close()


# ----------------------------------------------------------------- chat
def ensure_chat_session(session_id: str, user_id: int | None = None) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO chat_sessions (session_id, user_id, created_at) VALUES (?, ?, ?)",
            (session_id, user_id, now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def chat_session_exists(session_id: str) -> bool:
    conn = get_conn()
    try:
        return conn.execute("SELECT 1 FROM chat_sessions WHERE session_id = ?", (session_id,)).fetchone() is not None
    finally:
        conn.close()


def add_chat_message(session_id: str, role: str, content: str, metadata: dict | None = None) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, json.dumps(metadata) if metadata else None, now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def get_chat_messages(session_id: str) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT role, content, metadata FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
        result = []
        for r in rows:
            item = {"role": r["role"], "content": r["content"]}
            if r["role"] == "assistant" and r["metadata"]:
                try:
                    item["metadata"] = json.loads(r["metadata"])
                except json.JSONDecodeError:
                    pass
            result.append(item)
        return result
    finally:
        conn.close()


# ---------------------------------------------------------------- cache
def cache_get(cache_key: str) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM llm_cache WHERE cache_key = ?", (cache_key,)).fetchone()
        if row is None:
            return None
        return {"reply": row["reply"], "model": row["model"],
                "input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"]}
    finally:
        conn.close()


def cache_put(cache_key: str, reply: str, model: str, input_tokens: int, output_tokens: int) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO llm_cache (cache_key, reply, model, input_tokens, output_tokens, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (cache_key, reply, model, input_tokens, output_tokens, now_iso()),
        )
        conn.commit()
    finally:
        conn.close()
