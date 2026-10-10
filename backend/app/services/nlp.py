"""Classical NLP signals computed before the LLM sees the resume:
skill extraction (phrase matching), TF-IDF cosine similarity, and structure checks."""
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS: dict[str, list[str]] = {
    "Python": ["python"], "Java": ["java"], "JavaScript": ["javascript", "ecmascript"],
    "TypeScript": ["typescript"], "C++": ["c++"], "C#": ["c#"], "Go": ["golang"],
    "SQL": ["sql"], "PostgreSQL": ["postgresql", "postgres"], "MongoDB": ["mongodb"],
    "MySQL": ["mysql"], "Redis": ["redis"], "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs"], "Node.js": ["node.js", "nodejs"],
    "HTML": ["html", "html5"], "CSS": ["css", "css3"], "Tailwind": ["tailwind"],
    "FastAPI": ["fastapi"], "Django": ["django"], "Flask": ["flask"],
    "Spring Boot": ["spring boot", "springboot"], "REST APIs": ["rest", "restful", "rest api", "rest apis"],
    "GraphQL": ["graphql"], "Microservices": ["microservices"], "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"], "AWS": ["aws", "amazon web services"],
    "CI/CD": ["ci/cd", "cicd"], "Git": ["git", "github"], "Linux": ["linux"],
    "Machine Learning": ["machine learning"], "NLP": ["nlp", "natural language processing"],
    "LLMs": ["llm", "llms", "large language model", "large language models"],
    "Deep Learning": ["deep learning"], "PyTorch": ["pytorch"], "TensorFlow": ["tensorflow"],
    "Pandas": ["pandas"], "NumPy": ["numpy"], "OpenCV": ["opencv"],
    "Data Structures": ["data structures", "dsa"], "Algorithms": ["algorithms"],
    "System Design": ["system design"], "Testing": ["junit", "pytest", "unit testing", "jest"],
    "Agile": ["agile", "scrum"],
}

ROLE_PROFILES = {
    "backend": ["Python", "Java", "SQL", "PostgreSQL", "REST APIs", "Docker", "Git", "Data Structures", "System Design", "Testing"],
    "frontend": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "REST APIs", "Git", "Testing"],
    "full": ["JavaScript", "React", "Node.js", "SQL", "REST APIs", "Docker", "Git", "Data Structures", "Testing"],
    "data": ["Python", "SQL", "Pandas", "NumPy", "Machine Learning", "Git"],
    "machine": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "NumPy", "Pandas", "NLP", "Git"],
    "ai": ["Python", "Machine Learning", "LLMs", "NLP", "FastAPI", "Docker", "Git"],
    "devops": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Git", "Python"],
    "default": ["Data Structures", "Algorithms", "Git", "SQL", "REST APIs", "Testing"],
}

_PATTERNS = {
    name: re.compile(
        r"(?<![\w+#.])(?:" + "|".join(re.escape(a) for a in aliases) + r")(?![\w+#])", re.IGNORECASE
    )
    for name, aliases in SKILLS.items()
}
SECTIONS = ["summary", "experience", "education", "projects", "skills"]


def extract_skills(text: str) -> set[str]:
    return {name for name, pattern in _PATTERNS.items() if pattern.search(text)}


def expected_skills(role: str) -> set[str]:
    role = role.lower()
    for key, skills in ROLE_PROFILES.items():
        if key in role:
            return set(skills)
    return set(ROLE_PROFILES["default"])


def tfidf_similarity(a: str, b: str) -> float:
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    try:
        matrix = vec.fit_transform([a, b])
    except ValueError:  # empty vocabulary
        return 0.0
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def analyze(resume: str, role: str, job_description: str = "") -> dict:
    found = extract_skills(resume)
    target = extract_skills(job_description) if job_description.strip() else set()
    if not target:
        target = expected_skills(role)
    matched, missing = found & target, target - found
    coverage = len(matched) / len(target) if target else 0.0

    similarity = tfidf_similarity(resume, job_description) if job_description.strip() else None
    # Resume/JD cosine similarity rarely exceeds ~0.4, so scale it before blending.
    score = coverage if similarity is None else 0.7 * coverage + 0.3 * min(1.0, similarity * 2.5)

    lower = resume.lower()
    lines = [ln.strip() for ln in resume.splitlines() if len(ln.strip()) > 30]
    return {
        "match_score": round(score * 100),
        "skills_found": sorted(found),
        "skills_matched": sorted(matched),
        "skills_missing": sorted(missing),
        "similarity": None if similarity is None else round(similarity, 3),
        "sections_present": [s for s in SECTIONS if re.search(rf"^\s*{s}\b", lower, re.MULTILINE)],
        "quantified_lines": sum(1 for ln in lines if re.search(r"\d", ln)),
        "total_lines": len(lines),
        "word_count": len(resume.split()),
    }
