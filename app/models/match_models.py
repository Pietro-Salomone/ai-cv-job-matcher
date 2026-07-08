from enum import Enum

from pydantic import BaseModel, Field


class MatchLevel(str, Enum):
    low = "low"
    medium = "medium"
    good = "good"
    excellent = "excellent"


class ImpactLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class PriorityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class MatchAnalysisRequest(BaseModel):
    cv_text: str = Field(
        ...,
        min_length=50,
        description="Full text extracted from the candidate CV.",
    )
    job_description_text: str = Field(
        ...,
        min_length=50,
        description="Full text of the job description.",
    )
    language: str = Field(
        default="it",
        description="Language of the generated analysis. Example: it, en.",
    )


class SeniorityMatch(BaseModel):
    candidate_seniority: str
    required_seniority: str
    is_aligned: bool
    notes: str


class SkillMatch(BaseModel):
    matched: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    extra: list[str] = Field(default_factory=list)


class Gap(BaseModel):
    area: str
    description: str
    impact: ImpactLevel


class InterviewQuestion(BaseModel):
    question: str
    topic: str
    difficulty: DifficultyLevel


class StudyPlanItem(BaseModel):
    topic: str
    reason: str
    priority: PriorityLevel
    estimated_effort: str


class MatchAnalysisResponse(BaseModel):
    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall matching score from 0 to 100.",
    )
    match_level: MatchLevel
    candidate_summary: str
    job_summary: str
    seniority_match: SeniorityMatch
    technical_skills: SkillMatch
    soft_skills: SkillMatch
    main_gaps: list[Gap] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    interview_questions: list[InterviewQuestion] = Field(default_factory=list)
    study_plan: list[StudyPlanItem] = Field(default_factory=list)