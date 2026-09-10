from dataclasses import dataclass


@dataclass
class ClassifiedDocuments:
    jd: tuple[str, str]
    resumes: list[tuple[str, str]]


class ClassificationError(ValueError):
    pass


def classify_document_type(text: str, filename: str = "") -> str:
    filename_hint = filename.lower().replace("_", " ").replace("-", " ")
    lowered = text.lower()
    jd_score = _jd_score(text)
    resume_score = _resume_score(text)
    if any(marker in filename_hint for marker in ("job description", "job", "jd", "vacancy", "role")):
        jd_score += 3
    if any(marker in filename_hint for marker in ("resume", "cv", "curriculum vitae", "candidate")):
        resume_score += 3
    has_jd_structure = "responsibilities" in lowered and any(
        marker in lowered for marker in ("required skills", "qualifications", "requirements")
    )
    if has_jd_structure or (jd_score >= 2 and jd_score > resume_score):
        return "jd"
    if resume_score >= 2 and resume_score > jd_score:
        return "resume"
    return "unknown"


def is_resume_like(text: str) -> bool:
    """Return whether the document has enough candidate-profile evidence."""
    return _resume_score(text) >= 2 and _jd_score(text) < 2


def classify_documents(documents: list[tuple[str, str]]) -> ClassifiedDocuments:
    if len(documents) < 2:
        raise ClassificationError("Upload one job description and at least one resume.")

    scored = [(filename, text, _jd_score(text)) for filename, text in documents]
    scored.sort(key=lambda item: item[2], reverse=True)
    best = scored[0]
    second = scored[1]
    if best[2] >= 2 and second[2] >= 2:
        raise ClassificationError("I found more than one possible job description. Upload only one JD and then upload the resumes.")
    if best[2] == 0 or best[2] == second[2]:
        filename = next((name for name, _ in documents if "jd" in name.lower() or "job" in name.lower()), None)
        if filename:
            best = next(item for item in scored if item[0] == filename)
        else:
            raise ClassificationError("I could not confidently identify the job description. Rename it with 'JD' or 'job', then try again.")

    resumes = [(filename, text) for filename, text, _ in scored if filename != best[0]]
    unrelated = [filename for filename, text in resumes if _resume_score(text) < 2]
    if unrelated:
        names = ", ".join(unrelated)
        raise ClassificationError(f"These file(s) do not look like resumes: {names}. Upload candidate resumes or remove them.")
    return ClassifiedDocuments(jd=(best[0], best[1]), resumes=resumes)


def _jd_score(text: str) -> int:
    lowered = text.lower()
    markers = (
        "responsibilities", "requirements", "qualifications", "job description",
        "preferred", "required skills", "what you will do", "years of experience",
    )
    return sum(lowered.count(marker) for marker in markers)


def _resume_score(text: str) -> int:
    lowered = text.lower()
    markers = (
        "skills", "experience", "education", "employment", "work history",
        "projects", "certifications", "objective", "resume", "curriculum vitae",
    )
    return sum(lowered.count(marker) for marker in markers)
