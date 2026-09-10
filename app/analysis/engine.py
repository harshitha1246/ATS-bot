from app.analysis.gap_analyzer import prioritize_gaps
from app.analysis.jd_parser import parse_job_description
from app.analysis.matcher import match_skills
from app.analysis.models import JobDescription, ResumeAnalysis
from app.analysis.recommender import course_link_details, recommend_courses
from app.analysis.resume_parser import parse_resume
from app.analysis.scorer import WEIGHTS, calculate_score


def analyze_resume(jd: JobDescription, filename: str, text: str) -> ResumeAnalysis:
    resume = parse_resume(filename, text)
    matched, missing, important = match_skills(jd, resume)
    score, factors = calculate_score(jd, resume, matched)
    gaps = prioritize_gaps(jd, resume, important)
    recommendation_gaps = list(gaps)
    if factors["experience"] < 1.0 and "Practical project experience" not in recommendation_gaps:
        recommendation_gaps.append("Practical project experience")
    gap_explanations = _explain_gaps(jd, gaps)
    alignment = round(score * 0.85 + factors["responsibilities"] * 15)
    rating = "High" if alignment >= 75 else "Medium" if alignment >= 55 else "Low"
    return ResumeAnalysis(
        resume_name=filename,
        score=score,
        matched_skills=matched,
        missing_skills=missing,
        important_gaps=gaps,
        alignment_percentage=alignment,
        alignment_rating=rating,
        explanation=_explain(rating, factors),
        course_recommendations=recommend_courses(recommendation_gaps),
        skill_details={"required": [item.name for item in jd.required_requirements], "preferred": [item.name for item in jd.preferred_requirements]},
        gap_explanations=gap_explanations,
        score_breakdown={name: round(factors[name] * weight * 100) for name, weight in WEIGHTS.items()},
        course_links=course_link_details(recommendation_gaps),
    )


def analyze_documents(jd_text: str, resumes: list[tuple[str, str]]) -> list[ResumeAnalysis]:
    jd = parse_job_description(jd_text)
    analyses = []
    for filename, text in resumes:
        try:
            analyses.append(analyze_resume(jd, filename, text))
        except Exception as exc:
            analyses.append(_failed_analysis(filename, str(exc)))
    return sorted(analyses, key=lambda item: item.score, reverse=True)


def _explain(rating: str, factors: dict[str, float]) -> str:
    strongest = max(factors, key=factors.get)
    return f"{rating} alignment. The strongest measurable area is {strongest.replace('_', ' ')}. The score is based on the visible weighted factors below."


def _explain_gaps(jd: JobDescription, gaps: list[str]) -> list[str]:
    required = {item.name for item in jd.required_requirements}
    preferred = {item.name for item in jd.preferred_requirements}
    explanations = []
    for gap in gaps:
        if gap in required:
            explanations.append(f"{gap}: required by the JD, but no clear evidence was found in the resume.")
        elif gap in preferred:
            explanations.append(f"{gap}: preferred by the JD, but no clear evidence was found in the resume.")
        else:
            explanations.append(f"{gap}: this requirement could not be fully verified from the resume.")
    return explanations


def _failed_analysis(filename: str, error: str) -> ResumeAnalysis:
    return ResumeAnalysis(filename, 0, [], [], [f"Could not analyze this file: {error}"], 0, "Unavailable", "This resume was skipped without stopping the other analyses.", [], {"required": [], "preferred": []})
