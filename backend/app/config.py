"""Runtime configuration for the Career Guidance v2 backend.

All secrets come from environment variables. LLM_API_KEYS is a
comma-separated pool of provider keys (same convention as the Lyftr
assignment): the chat layer tries key_1, then key_2, ... with failover.
Placeholder / dummy keys are detected and treated as "no live LLM",
in which case the chatbot gracefully falls back to its built-in
knowledge-base answers so the site always works.
"""
import os


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DUMMY_PREFIXES = ("sk-dummy", "dummy", "test-", "sk-test", "placeholder", "your-", "xxxx", "key-", "changeme")


def is_dummy_key(key: str) -> bool:
    k = (key or "").strip().lower()
    return len(k) < 24 or any(k.startswith(p) for p in DUMMY_PREFIXES)


class Settings:
    def __init__(self) -> None:
        raw_keys = os.getenv("LLM_API_KEYS", "")
        self.llm_api_keys: list[str] = [k.strip() for k in raw_keys.split(",") if k.strip()]
        self.llm_model: str = os.getenv("LLM_MODEL", "gemini/gemini-3.5-flash-lite")
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./career_guidance.db")
        raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
        self.allowed_origins: list[str] = [o.strip() for o in raw_origins.split(",") if o.strip()] or ["*"]
        self.jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me-in-production")
        self.jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
        self.enable_failure_simulation: bool = _bool(os.getenv("ENABLE_FAILURE_SIMULATION", "true"))
        self.cache_enabled: bool = True

    @property
    def real_keys(self) -> list[str]:
        """Keys that look like genuine provider keys (not placeholders)."""
        return [k for k in self.llm_api_keys if not is_dummy_key(k)]

    @property
    def keys_configured(self) -> int:
        return len(self.real_keys)

    @property
    def llm_available(self) -> bool:
        return self.keys_configured > 0


settings = Settings()
