from app.analysis.models import JobDescription, ResumeProfile


def prioritize_gaps(jd: JobDescription, resume: ResumeProfile, important_missing: list[str]) -> list[str]:
    gaps = list(important_missing)
    required_experience = next((int(item.name.split("+")[0]) for item in jd.requirements if item.category == "experience"), None)
    if required_experience is not None and (resume.years_experience is None or resume.years_experience < required_experience):
        gaps.append(f"At least {required_experience} years of experience")
    return gaps[:8]
