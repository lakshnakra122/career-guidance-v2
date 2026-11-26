"""Curated career data for the Career Guidance v2 system.

Extends the v1 recommendation data with richer metadata (descriptions,
India salary outlook, demand trend) and a fuller course catalogue so the
skill-gap engine can recommend a course for almost every gap skill.
"""
from typing import Dict, List

# Assessment features (0-10 self-ratings), same 8 dimensions as v1.
FEATURES = ["math", "logical_reasoning", "creativity", "communication",
            "programming", "data_interest", "design_interest", "business_interest"]

FEATURE_LABELS = {
    "math": "Mathematics",
    "logical_reasoning": "Logical Reasoning",
    "creativity": "Creativity",
    "communication": "Communication",
    "programming": "Programming",
    "data_interest": "Interest in Data",
    "design_interest": "Interest in Design",
    "business_interest": "Interest in Business",
}

# Idealised feature profile per career (0-10) — the pattern the ML model learns.
CAREER_PROFILES: Dict[str, List[int]] = {
    "ML Engineer": [9, 9, 5, 6, 9, 9, 3, 4],
    "Data Scientist": [9, 8, 6, 7, 7, 10, 4, 6],
    "Full-Stack Developer": [6, 8, 6, 6, 10, 4, 6, 5],
    "Data Analyst": [8, 7, 5, 8, 6, 9, 4, 7],
    "UI/UX Designer": [4, 6, 10, 8, 5, 3, 10, 6],
    "DevOps Engineer": [6, 9, 4, 6, 9, 4, 3, 5],
    "Cybersecurity Analyst": [7, 9, 5, 6, 8, 5, 3, 4],
    "AI Researcher": [10, 10, 7, 6, 8, 9, 3, 3],
}

CAREER_SKILLS: Dict[str, List[str]] = {
    "ML Engineer": ["Python", "Machine Learning", "Deep Learning", "Mathematics",
                    "Data Structures", "MLOps", "SQL"],
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "Data Visualization",
                       "SQL", "Pandas", "Storytelling"],
    "Full-Stack Developer": ["HTML/CSS", "JavaScript", "React", "Node.js",
                             "REST APIs", "Databases", "Git"],
    "Data Analyst": ["SQL", "Excel", "Python", "Data Visualization", "Statistics",
                     "Business Acumen"],
    "UI/UX Designer": ["Design Thinking", "Figma", "User Research", "Wireframing",
                       "Prototyping", "HTML/CSS"],
    "DevOps Engineer": ["Linux", "Git", "Docker", "Kubernetes", "CI/CD", "Cloud (AWS)",
                        "Scripting"],
    "Cybersecurity Analyst": ["Networking", "Linux", "Security Fundamentals",
                              "Python", "Ethical Hacking", "SIEM Tools"],
    "AI Researcher": ["Mathematics", "Deep Learning", "Python", "Research Methods",
                      "PyTorch", "Paper Reading"],
}

# Salary figures are indicative fresher ranges for India (2025-26), in LPA.
CAREER_META: Dict[str, Dict] = {
    "ML Engineer": {
        "tagline": "Build and ship machine-learning models that power real products.",
        "salary_min_lpa": 9, "salary_max_lpa": 16, "demand": "Very High",
        "growth": "+36% YoY openings",
    },
    "Data Scientist": {
        "tagline": "Turn data into decisions with statistics, ML and storytelling.",
        "salary_min_lpa": 8, "salary_max_lpa": 14, "demand": "Very High",
        "growth": "+32% YoY openings",
    },
    "Full-Stack Developer": {
        "tagline": "Build complete web apps — frontend, backend and everything between.",
        "salary_min_lpa": 5, "salary_max_lpa": 9, "demand": "High",
        "growth": "+24% YoY openings",
    },
    "Data Analyst": {
        "tagline": "Answer business questions with SQL, dashboards and clear insights.",
        "salary_min_lpa": 4, "salary_max_lpa": 7, "demand": "High",
        "growth": "+27% YoY openings",
    },
    "UI/UX Designer": {
        "tagline": "Design products people love through research, wireframes and prototypes.",
        "salary_min_lpa": 4, "salary_max_lpa": 8, "demand": "High",
        "growth": "+21% YoY openings",
    },
    "DevOps Engineer": {
        "tagline": "Automate how software is built, tested and run in the cloud.",
        "salary_min_lpa": 6, "salary_max_lpa": 10, "demand": "Very High",
        "growth": "+29% YoY openings",
    },
    "Cybersecurity Analyst": {
        "tagline": "Protect systems and data by finding weaknesses before attackers do.",
        "salary_min_lpa": 5, "salary_max_lpa": 9, "demand": "Very High",
        "growth": "+33% YoY openings",
    },
    "AI Researcher": {
        "tagline": "Push the frontier of AI with experiments, papers and new models.",
        "salary_min_lpa": 10, "salary_max_lpa": 18, "demand": "High",
        "growth": "+30% YoY openings",
    },
}

COURSES: Dict[str, List[Dict[str, str]]] = {
    "Python": [{"title": "Python for Everybody", "provider": "Coursera", "link": "https://www.coursera.org/specializations/python"}],
    "Machine Learning": [{"title": "Machine Learning Specialization", "provider": "Coursera / Andrew Ng", "link": "https://www.coursera.org/specializations/machine-learning-introduction"}],
    "Deep Learning": [{"title": "Deep Learning Specialization", "provider": "Coursera", "link": "https://www.coursera.org/specializations/deep-learning"}],
    "Mathematics": [{"title": "Mathematics for Machine Learning", "provider": "Coursera", "link": "https://www.coursera.org/specializations/mathematics-machine-learning"}],
    "Data Structures": [{"title": "Data Structures and Algorithms", "provider": "Coursera / UC San Diego", "link": "https://www.coursera.org/specializations/data-structures-algorithms"}],
    "MLOps": [{"title": "Machine Learning Engineering for Production (MLOps)", "provider": "Coursera", "link": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"}],
    "SQL": [{"title": "SQL for Data Science", "provider": "Coursera", "link": "https://www.coursera.org/learn/sql-for-data-science"}],
    "Statistics": [{"title": "Statistics with Python", "provider": "Coursera", "link": "https://www.coursera.org/specializations/statistics-with-python"}],
    "Data Visualization": [{"title": "Data Visualization with Python", "provider": "Coursera", "link": "https://www.coursera.org/learn/python-for-data-visualization"}],
    "Pandas": [{"title": "Data Analysis with Python", "provider": "freeCodeCamp", "link": "https://www.freecodecamp.org/learn/data-analysis-with-python/"}],
    "Storytelling": [{"title": "Data Storytelling", "provider": "Coursera", "link": "https://www.coursera.org/learn/data-storytelling"}],
    "HTML/CSS": [{"title": "Responsive Web Design", "provider": "freeCodeCamp", "link": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"}],
    "JavaScript": [{"title": "JavaScript Algorithms and Data Structures", "provider": "freeCodeCamp", "link": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/"}],
    "React": [{"title": "React - The Complete Guide", "provider": "Udemy", "link": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"}],
    "Node.js": [{"title": "The Complete Node.js Developer Course", "provider": "Udemy", "link": "https://www.udemy.com/course/the-complete-node-developer-course-2/"}],
    "REST APIs": [{"title": "APIs and Microservices", "provider": "freeCodeCamp", "link": "https://www.freecodecamp.org/learn/back-end-development-and-apis/"}],
    "Databases": [{"title": "Databases and SQL for Data Science", "provider": "Coursera / IBM", "link": "https://www.coursera.org/learn/sql-data-science"}],
    "Git": [{"title": "Git and GitHub for Beginners", "provider": "freeCodeCamp (YouTube)", "link": "https://www.youtube.com/watch?v=RGOj5yH7evk"}],
    "Excel": [{"title": "Excel Skills for Business", "provider": "Coursera / Macquarie", "link": "https://www.coursera.org/specializations/excel"}],
    "Business Acumen": [{"title": "Business Foundations", "provider": "Coursera / Wharton", "link": "https://www.coursera.org/specializations/wharton-business-foundations"}],
    "Design Thinking": [{"title": "Design Thinking for Innovation", "provider": "Coursera / UVA Darden", "link": "https://www.coursera.org/learn/design-thinking-innovation"}],
    "Figma": [{"title": "Figma UI UX Design Essentials", "provider": "Udemy", "link": "https://www.udemy.com/course/figma-ux-ui-design-user-interface-design-websites/"}],
    "User Research": [{"title": "User Experience Research and Design", "provider": "Coursera / Michigan", "link": "https://www.coursera.org/specializations/user-experience-research-and-design"}],
    "Wireframing": [{"title": "UX Design Fundamentals", "provider": "Coursera / CalArts", "link": "https://www.coursera.org/specializations/ux-design-fundamentals"}],
    "Prototyping": [{"title": "Google UX Design Certificate", "provider": "Coursera / Google", "link": "https://www.coursera.org/professional-certificates/google-ux-design"}],
    "Linux": [{"title": "Linux Command Line Basics", "provider": "Udemy", "link": "https://www.udemy.com/course/linux-command-line-volume1/"}],
    "Docker": [{"title": "Docker Mastery", "provider": "Udemy", "link": "https://www.udemy.com/course/docker-mastery/"}],
    "Kubernetes": [{"title": "Kubernetes for Beginners", "provider": "Udemy", "link": "https://www.udemy.com/course/learn-kubernetes/"}],
    "CI/CD": [{"title": "CI/CD with GitHub Actions", "provider": "GitHub Skills", "link": "https://skills.github.com/"}],
    "Cloud (AWS)": [{"title": "AWS Cloud Practitioner Essentials", "provider": "AWS Skill Builder", "link": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"}],
    "Scripting": [{"title": "Bash Scripting and Shell Programming", "provider": "Udemy", "link": "https://www.udemy.com/course/bash-scripting-and-shell-programming/"}],
    "Networking": [{"title": "Computer Networking Fundamentals", "provider": "Coursera / Google IT Support", "link": "https://www.coursera.org/learn/computer-networking"}],
    "Security Fundamentals": [{"title": "Google Cybersecurity Certificate", "provider": "Coursera / Google", "link": "https://www.coursera.org/professional-certificates/google-cybersecurity"}],
    "Ethical Hacking": [{"title": "Learn Ethical Hacking From Scratch", "provider": "Udemy", "link": "https://www.udemy.com/course/learn-ethical-hacking-from-scratch/"}],
    "SIEM Tools": [{"title": "SIEM Fundamentals with Splunk", "provider": "Splunk Education", "link": "https://www.splunk.com/en_us/training.html"}],
    "Research Methods": [{"title": "Research Methods", "provider": "Coursera / SOAS", "link": "https://www.coursera.org/learn/research-methods"}],
    "PyTorch": [{"title": "Deep Learning with PyTorch", "provider": "Udemy", "link": "https://www.udemy.com/course/pytorch-for-deep-learning/"}],
    "Paper Reading": [{"title": "How to Read a Research Paper", "provider": "Self-guided (arXiv practice)", "link": "https://arxiv.org/"}],
}

PROJECT_IDEAS: Dict[str, List[str]] = {
    "ML Engineer": ["End-to-end house-price predictor with FastAPI deployment",
                    "Image classifier with transfer learning + MLOps pipeline",
                    "Movie recommender system with collaborative filtering"],
    "Data Scientist": ["Customer churn analysis with full EDA report",
                       "Sales forecasting dashboard",
                       "NLP sentiment analysis on product reviews"],
    "Full-Stack Developer": ["Personal portfolio + blog with auth",
                             "E-commerce clone with cart and payments (test mode)",
                             "Real-time chat app with WebSockets"],
    "Data Analyst": ["IPL/retail sales dashboard in Power BI",
                     "Excel + SQL business KPI report",
                     "A/B test analysis case study"],
    "UI/UX Designer": ["Redesign a college app — case study with user research",
                       "Design system + component library in Figma",
                       "Mobile app prototype for a campus problem"],
    "DevOps Engineer": ["CI/CD pipeline for a sample app (GitHub Actions)",
                        "Dockerized microservices on Kubernetes (minikube)",
                        "Infrastructure as code with Terraform on free tier"],
    "Cybersecurity Analyst": ["Home lab: vulnerability scan + report",
                              "Python port scanner + log analyzer",
                              "TryHackMe beginner path write-ups"],
    "AI Researcher": ["Reproduce a classic paper (e.g. ResNet) in PyTorch",
                      "Literature review on a niche topic",
                      "Small novel experiment + arXiv-style report"],
}

# Knowledge base for the chatbot's offline (fallback) answers.
KNOWLEDGE_BASE: List[Dict[str, str]] = [
    {"topic": "ML Engineer roadmap",
     "text": "To become an ML Engineer: 1) Master Python and DSA. 2) Learn maths (linear algebra, probability, statistics). "
             "3) Take Andrew Ng's Machine Learning Specialization. 4) Learn deep learning (PyTorch). 5) Build 2-3 end-to-end "
             "projects with deployment (FastAPI + Docker). 6) Learn MLOps basics (MLflow, CI/CD). Typical timeline: 6-9 months at 10 hrs/week."},
    {"topic": "Data Scientist roadmap",
     "text": "To become a Data Scientist: 1) Python (pandas, numpy). 2) Statistics and probability. 3) SQL. "
             "4) Data visualization (matplotlib, Power BI). 5) Machine learning basics. 6) Portfolio of EDA + modelling case studies. "
             "Strong communication/storytelling matters as much as modelling."},
    {"topic": "Full-Stack Developer roadmap",
     "text": "To become a Full-Stack Developer: 1) HTML, CSS, JavaScript. 2) React for frontend. 3) Node.js + Express for backend. "
             "4) REST APIs and databases (MongoDB/PostgreSQL). 5) Git and deployment (Vercel/Render). Build 3-4 complete apps for your portfolio."},
    {"topic": "Choosing a career",
     "text": "Take the skill & interest assessment on this platform: it scores maths, logic, creativity, communication, programming "
             "and interests, then the ML model predicts your top-3 career domains with match percentages. Love maths + code -> ML/Data roles. "
             "Love design + empathy -> UI/UX. Love building things end-to-end -> Full-Stack."},
    {"topic": "Skill gap",
     "text": "A skill gap is the difference between the skills a career requires and the skills you currently have. "
             "This platform compares your profile against each career's required skills, lists the missing ones, and recommends "
             "specific courses and projects to close each gap, plus a week-by-week roadmap."},
    {"topic": "Fresher salaries India",
     "text": "Indicative fresher CTCs in India (2025-26): Data Analyst 4-7 LPA, Full-Stack Developer 5-9 LPA, "
             "DevOps Engineer 6-10 LPA, Data Scientist 8-14 LPA, ML Engineer 9-16 LPA, AI Researcher 10-18 LPA. "
             "Product companies and strong portfolios pay above these bands."},
    {"topic": "Projects for resume",
     "text": "Recruiters value 2-3 complete projects over many tutorials. Each project should have: a clear problem statement, "
             "your tech stack, 3-5 bullet points of what YOU built, and a live link + GitHub repo."},
    {"topic": "How the AI works",
     "text": "This system has three AI parts: 1) A scikit-learn RandomForest model trained on assessment data predicts "
             "your career domain with match percentages. 2) A recommendation engine does skill-gap analysis and suggests courses, "
             "projects and roadmaps. 3) An LLM-powered chatbot (with multi-key failover and response caching) answers career "
             "questions, and falls back to a built-in knowledge base when the LLM is unavailable."},
    {"topic": "Study plan tips",
     "text": "A good study plan: fix 1-2 hours daily instead of weekend marathons, learn one skill at a time in roadmap order, "
             "build a mini-project after every skill, and revise weekly. Use the Study Plan page to generate a personalised "
             "6-week schedule based on your available hours."},
]
