import re

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "postgres sql": "postgresql",
    "restful api": "rest api",
    "restful apis": "rest api",
    "amazon web services": "aws",
    "continuous integration": "ci/cd",
}

KNOWN_SKILLS = {
    "python", "javascript", "typescript", "java", "c#", "c++", "sql", "postgresql",
    "mysql", "mongodb", "redis", "aws", "azure", "gcp", "docker", "kubernetes",
    "fastapi", "django", "flask", "react", "node.js", "rest api", "graphql", "git",
    "ci/cd", "linux", "pandas", "numpy", "scikit-learn", "machine learning", "llm",
    "communication", "testing", "pytest", "agile", "spark", "tableau", "power bi",
}


def normalize_skill(skill: str) -> str:
    cleaned = re.sub(r"\s+", " ", skill.lower().strip(" .,:;()[]{}"))
    return SKILL_ALIASES.get(cleaned, cleaned)


def extract_skills(text: str) -> set[str]:
    lowered = text.lower()
    found = set()
    for skill in KNOWN_SKILLS:
        pattern = rf"(?<![a-z0-9+#]){re.escape(skill)}(?![a-z0-9+#])"
        if re.search(pattern, lowered):
            found.add(normalize_skill(skill))
    return found
