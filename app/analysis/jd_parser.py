import re

from app.analysis.models import JobDescription, Requirement
from app.analysis.skill_normalizer import extract_skills


def parse_job_description(text: str) -> JobDescription:
    lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]
    title = lines[0][:100] if lines else "Untitled role"
    preferred_text = _text_after_heading(text, ("preferred", "nice to have", "bonus"))
    preferred_skills = extract_skills(preferred_text)
    requirements = [
        Requirement(skill, "preferred" if skill in preferred_skills else "required", "skill")
        for skill in sorted(extract_skills(text))
    ]
    years = re.findall(r"(\d+)\+?\s+years?", text, flags=re.IGNORECASE)
    if years:
        requirements.append(Requirement(f"{years[0]}+ years experience", "required", "experience"))
    responsibilities = _section_lines(text, ("responsibilities", "what you will do", "duties"))
    qualifications = _section_lines(text, ("qualifications", "requirements", "required skills"))
    return JobDescription(title, requirements, responsibilities, qualifications, text)


def _section_lines(text: str, headings: tuple[str, ...]) -> list[str]:
    lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]
    output = []
    active = False
    for line in lines:
        lowered = line.lower().rstrip(":")
        if any(heading in lowered for heading in headings):
            active = True
            continue
        if active and line.endswith(":") and len(line.split()) < 8:
            break
        if active:
            output.append(line)
    return output[:12]


def _text_after_heading(text: str, headings: tuple[str, ...]) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if any(heading in line.lower() for heading in headings):
            return "\n".join(lines[index + 1 :])
    return ""
