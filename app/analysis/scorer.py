from app.analysis.matcher import responsibility_alignment
from app.analysis.models import JobDescription, ResumeProfile

WEIGHTS = {
    "required_skills": 0.40,
    "preferred_skills": 0.15,
    "experience": 0.15,
    "education": 0.10,
    "responsibilities": 0.15,
    "keyword_relevance": 0.05,
}


def calculate_score(jd: JobDescription, resume: ResumeProfile, matched: list[str]) -> tuple[int, dict[str, float]]:
    required = [item.name for item in jd.required_requirements if item.category == "skill"]
    preferred = [item.name for item in jd.preferred_requirements if item.category == "skill"]
    matched_lower = {item.lower() for item in matched}
    required_ratio = _ratio([item.lower() for item in required], matched_lower)
    preferred_ratio = _ratio([item.lower() for item in preferred], matched_lower)
    experience_ratio = _experience_ratio(jd, resume)
    education_ratio = 1.0 if resume.education and jd.qualifications else 0.5
    responsibility_ratio = responsibility_alignment(jd, resume)
    relevance_ratio = min(1.0, len(matched) / max(1, len(required) + len(preferred)))
    factors = {
        "required_skills": required_ratio,
        "preferred_skills": preferred_ratio,
        "experience": experience_ratio,
        "education": education_ratio,
        "responsibilities": responsibility_ratio,
        "keyword_relevance": relevance_ratio,
    }
    score = round(sum(factors[name] * weight for name, weight in WEIGHTS.items()) * 100)
    return max(0, min(100, score)), factors


def _ratio(expected: list[str], actual: set[str]) -> float:
    return sum(item in actual for item in expected) / len(expected) if expected else 1.0


def _experience_ratio(jd: JobDescription, resume: ResumeProfile) -> float:
    required_years = next((int(item.name.split("+")[0]) for item in jd.requirements if item.category == "experience"), None)
    if required_years is None:
        return 1.0
    if resume.years_experience is None:
        return 0.0
    return min(1.0, resume.years_experience / required_years)
