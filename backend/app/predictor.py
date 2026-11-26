"""Career prediction engine (v2).

Improvements over v1:
- v1 required a pre-trained career_model.pkl on disk; if the file was
  missing the endpoint crashed. v2 trains the RandomForest in memory at
  startup on the synthetic dataset generated from the career profiles
  (same ground-truth patterns as v1), so prediction always works.
- Match percentages are calibrated: raw model probabilities are blended
  with profile-similarity and the student's existing-skill overlap, which
  produces more realistic, spread-out match % values for the UI.
- If scikit-learn is unavailable, a pure-Python similarity scorer takes
  over — the endpoint never goes down.
"""
import math
import threading

from .data import CAREER_PROFILES, CAREER_SKILLS, FEATURES

_model = None
_model_lock = threading.Lock()
_model_ready = False


def _train_in_memory():
    """Train the RandomForest on synthetic samples around each career profile."""
    global _model, _model_ready
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier

        rng = np.random.default_rng(42)
        X, y = [], []
        for career, profile in CAREER_PROFILES.items():
            for _ in range(80):
                sample = np.clip(np.array(profile, dtype=float) + rng.normal(0, 1.6, len(FEATURES)), 0, 10)
                X.append(sample)
                y.append(career)
        clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        clf.fit(X, y)
        _model = clf
    except Exception:
        _model = None
    _model_ready = True


def _ensure_model():
    if not _model_ready:
        with _model_lock:
            if not _model_ready:
                _train_in_memory()


def _similarity_scores(scores: dict) -> dict[str, float]:
    """Gaussian similarity of the student's vector to each career profile."""
    vec = [float(scores.get(f, 5)) for f in FEATURES]
    out = {}
    for career, profile in CAREER_PROFILES.items():
        dist2 = sum((a - b) ** 2 for a, b in zip(vec, profile))
        out[career] = math.exp(-dist2 / 60.0)  # bandwidth tuned for 0-10 scales
    total = sum(out.values()) or 1.0
    return {k: v / total for k, v in out.items()}


def _skill_overlap_boost(career: str, student_skills: list[str]) -> float:
    if not student_skills:
        return 0.0
    required = {s.lower() for s in CAREER_SKILLS.get(career, [])}
    have = {s.strip().lower() for s in student_skills if s.strip()}
    if not required:
        return 0.0
    return len(required & have) / len(required)


def predict_top_careers(scores: dict, student_skills: list[str] | None = None, top_n: int = 3) -> list[dict]:
    """Return the top-N careers with calibrated match percentages."""
    student_skills = student_skills or []
    _ensure_model()

    sim = _similarity_scores(scores)
    if _model is not None:
        row = [[float(scores.get(f, 5)) for f in FEATURES]]
        proba = _model.predict_proba(row)[0]
        ml = {c: float(p) for c, p in zip(_model.classes_, proba)}
        blended = {c: 0.55 * ml.get(c, 0.0) + 0.35 * sim.get(c, 0.0)
                   + 0.10 * _skill_overlap_boost(c, student_skills)
                   for c in CAREER_PROFILES}
    else:
        blended = {c: 0.85 * sim.get(c, 0.0) + 0.15 * _skill_overlap_boost(c, student_skills)
                   for c in CAREER_PROFILES}

    total = sum(blended.values()) or 1.0
    ranked = sorted(blended.items(), key=lambda kv: kv[1], reverse=True)
    return [
        {"career": career, "match_pct": round(100.0 * value / total, 1)}
        for career, value in ranked[:top_n]
    ]


def engine_name() -> str:
    _ensure_model()
    return "random-forest" if _model is not None else "profile-similarity"
