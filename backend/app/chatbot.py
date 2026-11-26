"""Career-guidance chatbot brain.

Builds a context-aware system prompt (student profile + predicted careers
+ retrieved knowledge-base passages) for the live LLM, and provides the
offline fallback answer used when no LLM keys are configured or every
provider attempt fails — so /chat always returns a useful reply.
"""
import re
from typing import Dict, List

from .data import KNOWLEDGE_BASE

BASE_SYSTEM_PROMPT = (
    "You are 'PathFinder AI', a friendly career-guidance assistant for Indian college students "
    "on the AI-Powered Personalized Learning and Career Recommendation platform. "
    "Give practical, encouraging, concise answers (2-6 short paragraphs or a short list). "
    "Use the student's profile, predicted careers and the knowledge excerpts when relevant. "
    "When asked for a roadmap or plan, give week-by-week steps. Mention indicative India "
    "fresher salary ranges (LPA) only when asked about pay. Never invent the student's data."
)


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z]{3,}", text.lower()))


def retrieve(question: str, top_k: int = 2) -> List[Dict[str, str]]:
    """Lightweight TF-IDF-style retrieval over the knowledge base.

    Uses scikit-learn when available (as v1 did); falls back to keyword
    overlap scoring so retrieval works in minimal environments too.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        docs = [d["topic"] + " " + d["text"] for d in KNOWLEDGE_BASE]
        vec = TfidfVectorizer().fit(docs + [question])
        q = vec.transform([question])
        D = vec.transform(docs)
        sims = cosine_similarity(q, D)[0]
        ranked = sorted(range(len(docs)), key=lambda i: sims[i], reverse=True)
        return [KNOWLEDGE_BASE[i] for i in ranked[:top_k] if sims[i] > 0.05]
    except Exception:
        q = _tokens(question)
        scored = []
        for d in KNOWLEDGE_BASE:
            overlap = len(q & _tokens(d["topic"] + " " + d["text"]))
            if overlap:
                scored.append((overlap, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]


def build_system_prompt(profile: dict | None, predictions: list | None) -> str:
    parts = [BASE_SYSTEM_PROMPT]
    profile = profile or {}
    if profile:
        bits = []
        if profile.get("skills"):
            bits.append("current skills: " + ", ".join(profile["skills"]))
        if profile.get("interests"):
            bits.append("interests: " + str(profile["interests"]))
        if profile.get("target_career"):
            bits.append("target career: " + str(profile["target_career"]))
        if profile.get("cgpa"):
            bits.append("CGPA: " + str(profile["cgpa"]))
        if bits:
            parts.append("Student profile — " + "; ".join(bits) + ".")
    if predictions:
        top = ", ".join(f"{p['career']} ({p['match_pct']}%)" for p in predictions[:3])
        parts.append(f"The student's latest assessment predicted top careers: {top}.")
    return "\n".join(parts)


def knowledge_context(question: str) -> str:
    docs = retrieve(question)
    if not docs:
        return ""
    return "Knowledge excerpts:\n" + "\n".join(f"- [{d['topic']}] {d['text']}" for d in docs)


def fallback_answer(question: str, profile: dict | None = None,
                    predictions: list | None = None) -> dict:
    """Offline answer from the knowledge base (+ the student's own data)."""
    docs = retrieve(question)
    low = question.lower()

    if predictions and any(w in low for w in ("my career", "my result", "my prediction", "suitable for me", "best career for me")):
        top = predictions[0]
        lines = ", ".join(f"{p['career']} ({p['match_pct']}%)" for p in predictions[:3])
        return {"answer": (f"Based on your latest assessment, your top career matches are: {lines}. "
                           f"Your strongest match is {top['career']} at {top['match_pct']}%. "
                           "Open the Roadmap page to get a week-by-week plan for it, or ask me anything about that career."),
                "sources": ["Your assessment"]}

    if docs:
        text = (f"Here's what I can tell you about **{docs[0]['topic']}**:\n\n{docs[0]['text']}")
        if len(docs) > 1:
            text += f"\n\nRelated: {docs[1]['text']}"
        text += "\n\n(Tip: I am currently answering from my built-in knowledge base. For fully personalised answers, an admin can connect an LLM key.)"
        return {"answer": text, "sources": [d["topic"] for d in docs]}

    return {"answer": ("I can help with career choices, roadmaps, skill gaps, study plans, fresher salaries in India "
                       "and resume projects. Try asking: 'What is the roadmap for a Data Scientist?' or "
                       "'Which career suits me?' — or take the Assessment first so I can personalise my answers."),
            "sources": []}
