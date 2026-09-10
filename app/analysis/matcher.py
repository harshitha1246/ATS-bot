from app.analysis.models import JobDescription, ResumeProfile
from app.analysis.skill_normalizer import normalize_skill


def match_skills(jd: JobDescription, resume: ResumeProfile) -> tuple[list[str], list[str], list[str]]:
    resume_skills = {normalize_skill(skill) for skill in resume.skills}
    required = [item.name for item in jd.required_requirements if item.category == "skill"]
    preferred = [item.name for item in jd.preferred_requirements if item.category == "skill"]
    matched = sorted(skill for skill in required + preferred if normalize_skill(skill) in resume_skills)
    missing = sorted(skill for skill in required + preferred if normalize_skill(skill) not in resume_skills)
    important = sorted(skill for skill in required if normalize_skill(skill) not in resume_skills)
    return matched, missing, important


def responsibility_alignment(jd: JobDescription, resume: ResumeProfile) -> float:
    if not jd.responsibilities or not resume.raw_text:
        return 0.0
    resume_text = resume.raw_text.lower()
    matches = sum(_shared_terms(item, resume_text) >= 2 for item in jd.responsibilities)
    return matches / len(jd.responsibilities)


def _shared_terms(sentence: str, text: str) -> int:
    terms = {word.lower() for word in sentence.split() if len(word) > 4}
    return sum(term in text for term in terms)
