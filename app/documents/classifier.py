from dataclasses import dataclass


@dataclass
class ClassifiedDocuments:
    jd: tuple[str, str]
    resumes: list[tuple[str, str]]


class ClassificationError(ValueError):
    pass


def classify_documents(documents: list[tuple[str, str]]) -> ClassifiedDocuments:
    if len(documents) < 2:
        raise ClassificationError("Upload one job description and at least one resume.")

    scored = [(filename, text, _jd_score(text)) for filename, text in documents]
    scored.sort(key=lambda item: item[2], reverse=True)
    best = scored[0]
    second = scored[1]
    if best[2] == 0 or best[2] == second[2]:
        filename = next((name for name, _ in documents if "jd" in name.lower() or "job" in name.lower()), None)
        if filename:
            best = next(item for item in scored if item[0] == filename)
        else:
            raise ClassificationError("I could not confidently identify the job description. Rename it with 'JD' or 'job', then try again.")

    resumes = [(filename, text) for filename, text, _ in scored if filename != best[0]]
    return ClassifiedDocuments(jd=(best[0], best[1]), resumes=resumes)


def _jd_score(text: str) -> int:
    lowered = text.lower()
    markers = (
        "responsibilities", "requirements", "qualifications", "job description",
        "preferred", "required skills", "what you will do", "years of experience",
    )
    return sum(lowered.count(marker) for marker in markers)
