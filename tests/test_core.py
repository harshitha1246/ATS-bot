from app.analysis.engine import analyze_documents
from app.analysis.jd_parser import parse_job_description
from app.analysis.matcher import match_skills
from app.analysis.engine import analyze_resume
from app.analysis.recommender import course_link_details, recommend_courses
from app.documents.classifier import ClassificationError, classify_document_type, classify_documents, is_jd_like, is_resume_like
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


def test_single_document_role_classification():
    assert classify_document_type(JD) == "jd"
    assert classify_document_type(RESUME) == "resume"
    assert classify_document_type("Chapter 4: unit conversion and measurement") == "unknown"


def test_upload_order_does_not_define_document_role():
    assert classify_document_type(RESUME) == "resume"
    assert classify_document_type(JD) == "jd"


def test_filename_hints_support_role_classification():
    assert classify_document_type(RESUME, "candidate_resume.pdf") == "resume"
    assert classify_document_type("Backend engineer with skills and experience", "Backend_JD.pdf") == "jd"
    assert is_resume_like(RESUME)
    assert not is_resume_like("Chapter 4: unit conversion and measurement")
    assert is_jd_like(JD, "job_description.pdf")
    assert not is_jd_like("Chapter 4: unit conversion and measurement", "unit_notes.pdf")


def test_ambiguous_classification_asks_for_clarification():
    try:
        classify_documents([("one.txt", "Python SQL"), ("two.txt", "Python SQL")])
        assert False
    except ClassificationError:
        assert True


def test_unrelated_document_is_not_treated_as_resume():
    try:
        classify_documents([("role.txt", JD), ("unit_notes.pdf", "Chapter 4: unit conversion and measurement")])
        assert False
    except ClassificationError as error:
        assert "do not look like resumes" in str(error)


def test_multiple_job_descriptions_are_rejected():
    second_jd = """Frontend Developer
    Responsibilities:
    Build user interfaces.
    Required Skills:
    JavaScript and React.
    """
    try:
        classify_documents([("backend_jd.txt", JD), ("frontend_jd.txt", second_jd)])
        assert False
    except ClassificationError as error:
        assert "more than one possible job description" in str(error)


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
    assert course_link_details(["AWS"])[0]["url"].startswith("https://")


def test_analysis_explains_gaps_and_score_contributions():
    jd = parse_job_description(JD)
    result = analyze_resume(jd, "partial.txt", "2 years experience. Skills: Python, SQL")
    assert result.gap_explanations
    assert result.score_breakdown
    assert all(value >= 0 for value in result.score_breakdown.values())


def test_course_recommendations_are_limited_to_four_links():
    result = analyze_resume(parse_job_description(JD), "partial.txt", "2 years experience. Skills: Python")
    assert len(result.course_links) <= 4


def test_multiple_resume_analysis_is_ranked():
    analyses = analyze_documents(JD, [("strong.txt", RESUME), ("partial.txt", "2 years experience. Skills: Python, SQL")])
    assert [item.resume_name for item in analyses] == ["strong.txt", "partial.txt"]
    assert analyses[0].score > analyses[1].score
    assert analyses[1].important_gaps
