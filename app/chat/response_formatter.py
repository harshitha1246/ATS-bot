from dataclasses import asdict

from app.analysis.models import ResumeAnalysis


def format_results(analyses: list[ResumeAnalysis]) -> dict:
    return {
        "ranking": [
            {"rank": index, "resume": item.resume_name, "score": item.score, "alignment": item.alignment_rating}
            for index, item in enumerate(analyses, 1)
        ],
        "analyses": [asdict(item) for item in analyses],
    }
