"""Recommendation engine v2: skill-gap analysis, courses, projects,
a week-by-week personalised roadmap and a study-plan generator.

v1 returned a 4-phase roadmap over 12 weeks. v2 produces an actionable
week-by-week plan (default 6 weeks): gap skills are sequenced across the
weeks in dependency-friendly order, each week carries concrete tasks, the
matching courses, and a checkpoint; the final week is projects + polish.
"""
from typing import Dict, List

from .data import CAREER_SKILLS, COURSES, PROJECT_IDEAS

# Rough learning order: foundations first so later skills build on them.
SKILL_PRIORITY = [
    "Python", "HTML/CSS", "Mathematics", "Statistics", "Linux", "Git",
    "Data Structures", "SQL", "JavaScript", "Excel", "Networking",
    "Design Thinking", "Pandas", "Data Visualization", "Machine Learning",
    "React", "Node.js", "REST APIs", "Databases", "Figma", "Wireframing",
    "User Research", "Prototyping", "Security Fundamentals", "Scripting",
    "Docker", "Deep Learning", "PyTorch", "Storytelling", "Business Acumen",
    "MLOps", "Kubernetes", "CI/CD", "Cloud (AWS)", "Ethical Hacking",
    "SIEM Tools", "Research Methods", "Paper Reading",
]


def _norm(skills: List[str]) -> set:
    return {s.strip().lower() for s in skills if s.strip()}


def skill_gap_analysis(student_skills: List[str], career: str) -> Dict:
    required = CAREER_SKILLS.get(career, [])
    have = _norm(student_skills)
    gaps = [s for s in required if s.lower() not in have]
    matched = [s for s in required if s.lower() in have]
    coverage = round(len(matched) / len(required) * 100) if required else 0
    return {"career": career, "required": required, "matched": matched,
            "gaps": gaps, "coverage_pct": coverage}


def recommend_courses(gaps: List[str]) -> List[Dict[str, str]]:
    out = []
    for skill in gaps:
        for c in COURSES.get(skill, []):
            out.append({"skill": skill, **c})
    return out


def recommend_projects(career: str) -> List[str]:
    return PROJECT_IDEAS.get(career, [])


def _ordered_gaps(gaps: List[str]) -> List[str]:
    def rank(skill: str) -> int:
        return SKILL_PRIORITY.index(skill) if skill in SKILL_PRIORITY else len(SKILL_PRIORITY)
    return sorted(gaps, key=rank)


def generate_roadmap(career: str, student_skills: List[str], weeks: int = 6) -> Dict:
    """Week-by-week plan. Gap skills are spread over weeks 1..N-1 in
    priority order; the last week is a portfolio project + interview prep.
    If there are no gaps, weeks focus on advanced projects instead."""
    gap = skill_gap_analysis(student_skills, career)
    gaps = _ordered_gaps(gap["gaps"])
    projects = recommend_projects(career)
    plan: List[Dict] = []

    if weeks < 2:
        weeks = 2
    skill_weeks = weeks - 1  # last week reserved for project/polish
    # Distribute gap skills round-robin by priority across skill weeks.
    buckets: List[List[str]] = [[] for _ in range(skill_weeks)]
    for i, skill in enumerate(gaps):
        buckets[i % skill_weeks].append(skill) if skill_weeks else None

    for w in range(skill_weeks):
        focus = buckets[w]
        if focus:
            title = "Learn: " + ", ".join(focus)
            tasks = [f"Complete the recommended course module for {s}" for s in focus]
            tasks.append("Practice exercises / notes for: " + ", ".join(focus))
            tasks.append("Build one mini exercise applying this week's skills")
            checkpoint = "You can explain and demo: " + ", ".join(focus)
        else:
            title = "Strengthen your existing skills"
            tasks = ["Revise your matched skills with advanced tutorials",
                     "Solve practice problems / design exercises",
                     "Start reading ahead on the project you will build in the final week"]
            checkpoint = "Confident with your current skill base; ready for the project week"
        plan.append({
            "week": w + 1,
            "title": title,
            "focus_skills": focus,
            "tasks": tasks,
            "courses": recommend_courses(focus),
            "checkpoint": checkpoint,
        })

    plan.append({
        "week": weeks,
        "title": "Portfolio project & placement polish",
        "focus_skills": [],
        "tasks": [
            f"Build this portfolio project: {projects[0]}" if projects else "Build a portfolio project",
            "Write a README with problem, stack and screenshots; push to GitHub",
            "Update your resume with the new skills and project",
            "Attempt 2 mock interviews / aptitude tests",
        ],
        "courses": [],
        "checkpoint": "Project live on GitHub + resume updated + mock interview attempted",
    })

    return {
        "career": career,
        "weeks": weeks,
        "coverage_pct": gap["coverage_pct"],
        "matched": gap["matched"],
        "gaps": gap["gaps"],
        "plan": plan,
    }


def generate_study_plan(career: str, student_skills: List[str],
                        hours_per_day: float = 2, days_per_week: int = 6,
                        weeks: int = 6) -> Dict:
    """Turn the roadmap into a daily study schedule with hour budgets."""
    roadmap = generate_roadmap(career, student_skills, weeks)
    weekly_hours = round(hours_per_day * days_per_week, 1)
    daily_routine = [
        {"block": "Learn", "share_pct": 50,
         "detail": "Watch course lessons / read docs for this week's focus skills"},
        {"block": "Practice", "share_pct": 30,
         "detail": "Hands-on exercises, coding problems or design drills"},
        {"block": "Build / Revise", "share_pct": 20,
         "detail": "Apply the skill in a mini task; revise the week's notes"},
    ]
    for block in daily_routine:
        block["minutes_per_day"] = int(hours_per_day * 60 * block["share_pct"] / 100)

    schedule = []
    for entry in roadmap["plan"]:
        schedule.append({
            "week": entry["week"],
            "title": entry["title"],
            "focus_skills": entry["focus_skills"],
            "hours_budget": weekly_hours,
            "checkpoint": entry["checkpoint"],
        })

    return {
        "career": career,
        "weeks": weeks,
        "hours_per_day": hours_per_day,
        "days_per_week": days_per_week,
        "total_hours": round(weekly_hours * weeks, 1),
        "daily_routine": daily_routine,
        "schedule": schedule,
        "tips": [
            "Keep the same time slot every day — consistency beats long weekend sessions.",
            "End each week by ticking off the checkpoint before moving on.",
            "If a week feels heavy, split its focus skills across two weeks instead of skipping practice.",
        ],
    }


def full_recommendation(student_skills: List[str], career: str) -> Dict:
    gap = skill_gap_analysis(student_skills, career)
    return {
        **gap,
        "courses": recommend_courses(gap["gaps"]),
        "projects": recommend_projects(career),
    }
