from app.analysis.engine import analyze_documents
from app.analysis.jd_parser import parse_job_description
from app.analysis.matcher import match_skills
from app.analysis.recommender import recommend_courses
from app.documents.classifier import ClassificationError, classify_documents
from app.documents.text_extractor import DocumentExtractionError, extract_text

JD = """Backend Python Developer
Responsibilities:
- Build REST APIs and write tests.
Required Skills:
Python, FastAPI, SQL, Docker
3+ years experience
Preferred Skills:
AWS
"""
RESUME = """Alex Candidate
4 years experience building Python services.
Skills: Python, FastAPI, SQL, Docker, AWS
Bachelor degree in Computer Science.
"""


def test_text_extraction_txt_and_invalid_file():
    assert "Python" in extract_text("resume.txt", RESUME.encode())
    try:
        extract_text("resume.exe", b"content")
        assert False
    except DocumentExtractionError:
        assert True


def test_classification_uses_content():
    result = classify_documents([("candidate.txt", RESUME), ("role.txt", JD)])
    assert result.jd[0] == "role.txt"
    assert result.resumes[0][0] == "candidate.txt"


def test_ambiguous_classification_asks_for_clarification():
    try:
        classify_documents([("one.txt", "Python SQL"), ("two.txt", "Python SQL")])
        assert False
    except ClassificationError:
        assert True


def test_matching_and_recommendations():
    jd = parse_job_description(JD)
    profile = parse_job_description(JD)
    assert profile.required_requirements
    from app.analysis.resume_parser import parse_resume
    matched, missing, important = match_skills(jd, parse_resume("resume.txt", RESUME))
    assert "python" in [item.lower() for item in matched]
    assert "aws" in [item.lower() for item in matched]
    assert not important
    assert recommend_courses(["Kubernetes"]) == ["Kubernetes for Developers"]


def test_multiple_resume_analysis_is_ranked():
    analyses = analyze_documents(JD, [("strong.txt", RESUME), ("partial.txt", "2 years experience. Skills: Python, SQL")])
    assert [item.resume_name for item in analyses] == ["strong.txt", "partial.txt"]
    assert analyses[0].score > analyses[1].score
    assert analyses[1].important_gaps
