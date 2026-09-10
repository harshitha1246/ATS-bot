from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Requirement:
    name: str
    importance: Literal["required", "preferred"] = "required"
    category: str = "skill"
    evidence: str = ""


@dataclass
class JobDescription:
    title: str
    requirements: list[Requirement] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    qualifications: list[str] = field(default_factory=list)
    raw_text: str = ""

    @property
    def required_requirements(self) -> list[Requirement]:
        return [item for item in self.requirements if item.importance == "required"]

    @property
    def preferred_requirements(self) -> list[Requirement]:
        return [item for item in self.requirements if item.importance == "preferred"]


@dataclass
class ResumeProfile:
    name: str
    skills: set[str] = field(default_factory=set)
    years_experience: float | None = None
    education: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    raw_text: str = ""


@dataclass
class ResumeAnalysis:
    resume_name: str
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    important_gaps: list[str]
    alignment_percentage: int
    alignment_rating: str
    explanation: str
    course_recommendations: list[str]
    skill_details: dict[str, list[str]]
