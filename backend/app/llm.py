"""LLM access via LiteLLM with multi-key failover (Lyftr pattern, adapted).

- Keys come from LLM_API_KEYS (comma-separated). Only keys that look real
  are used for live inference; placeholders are ignored.
- One attempt per key; 429 / 5xx failures fail over to the next key.
- If LiteLLM itself is missing, live inference is simply unavailable and
  the chatbot falls back to its knowledge base.
"""
import re

from .config import settings

try:
    import litellm

    LITELLM_AVAILABLE = True
except Exception:  # pragma: no cover - litellm missing in a minimal env
    litellm = None
    LITELLM_AVAILABLE = False

if LITELLM_AVAILABLE:
    # In-memory LiteLLM cache; a cache failure must never break inference.
    try:
        from litellm import Cache

        litellm.cache = Cache(type="local")
    except Exception:
        pass


class ProviderError(Exception):
    def __init__(self, status: int, message: str = "provider error"):
        super().__init__(message)
        self.status = status


def count_tokens(text: str) -> int:
    if not text:
        return 0
    if LITELLM_AVAILABLE:
        try:
            return int(litellm.token_counter(model=settings.llm_model, text=text))
        except Exception:
            pass
    return max(1, len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)))


def messages_token_count(messages: list[dict]) -> int:
    return sum(count_tokens(m.get("content", "")) for m in messages)


async def call_with_key(key: str, messages: list[dict]) -> tuple[str, int, int]:
    """One live attempt with one key. Returns (reply, input_tokens, output_tokens)."""
    if not LITELLM_AVAILABLE:
        raise ProviderError(503, "litellm unavailable")
    try:
        response = await litellm.acompletion(
            model=settings.llm_model,
            messages=messages,
            api_key=key,
            caching=True,
        )
    except Exception as exc:
        _msg = str(exc)
        for _k in settings.llm_api_keys:
            _msg = _msg.replace(_k, "***KEY***")
        print(f"LLM_CALL_ERROR type={type(exc).__name__} msg={_msg[:400]}", flush=True)
        text = str(exc).lower()
        status = 503
        if "429" in text or "rate" in text or "quota" in text:
            status = 429
        elif "500" in text:
            status = 500
        elif "502" in text:
            status = 502
        raise ProviderError(status, str(exc)) from exc

    reply = response.choices[0].message.content or ""
    if not reply.strip():
        raise ProviderError(503, "empty provider response")
    usage = getattr(response, "usage", None)
    input_tokens = int(getattr(usage, "prompt_tokens", 0) or messages_token_count(messages))
    output_tokens = int(getattr(usage, "completion_tokens", 0) or count_tokens(reply))
    return reply, input_tokens, output_tokens


def parse_simulate_failure(header: str | None) -> dict[str, int]:
    """'key_1=429,key_2=500' / '*=429' -> {'key_1': 429, ...}"""
    result: dict[str, int] = {}
    if not header:
        return result
    for part in header.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key_id, _, status = part.partition("=")
        try:
            code = int(status.strip())
        except ValueError:
            continue
        if code in {429, 500, 502, 503}:
            result[key_id.strip()] = code
    return result
