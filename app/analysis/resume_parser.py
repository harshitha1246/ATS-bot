import re

from app.analysis.models import ResumeProfile
from app.analysis.skill_normalizer import extract_skills


def parse_resume(filename: str, text: str) -> ResumeProfile:
    years_match = re.search(r"(\d+(?:\.\d+)?)\+?\s+years?", text, flags=re.IGNORECASE)
    education = [
        line.strip(" -•") for line in text.splitlines()
        if any(word in line.lower() for word in ("bachelor", "master", "degree", "b.tech", "m.tech", "phd"))
    ][:5]
    return ResumeProfile(
        name=filename,
        skills=extract_skills(text),
        years_experience=float(years_match.group(1)) if years_match else None,
        education=education,
        responsibilities=_resume_lines(text),
        raw_text=text,
    )


def _resume_lines(text: str) -> list[str]:
    return [line.strip(" -•") for line in text.splitlines() if len(line.strip()) > 35][:15]
