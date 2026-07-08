from app.ai.openai_client import OpenAIMatchAnalyzer
from app.core.config import settings
from app.models.match_models import (
    DifficultyLevel,
    Gap,
    ImpactLevel,
    InterviewQuestion,
    MatchAnalysisRequest,
    MatchAnalysisResponse,
    MatchLevel,
    PriorityLevel,
    SeniorityMatch,
    SkillMatch,
    StudyPlanItem,
)


def analyze_cv_job_match(request: MatchAnalysisRequest) -> MatchAnalysisResponse:
    """
    Analyze the match between a CV and a job description.

    If AI_PROVIDER=openai, this function calls the OpenAI API.
    Otherwise, it returns a mocked response.
    """

    if settings.ai_provider == "openai":
        analyzer = OpenAIMatchAnalyzer()
        return analyzer.analyze(request)

    return _build_mock_response()


def _build_mock_response() -> MatchAnalysisResponse:
    return MatchAnalysisResponse(
        match_score=78,
        match_level=MatchLevel.good,
        candidate_summary=(
            "Il candidato mostra un background tecnico solido, con esperienza "
            "nello sviluppo backend e interesse verso Python, FastAPI e AI generativa."
        ),
        job_summary=(
            "La posizione richiede competenze backend, capacità di lavorare con API, "
            "conoscenza di strumenti AI e familiarità con architetture moderne."
        ),
        seniority_match=SeniorityMatch(
            candidate_seniority="junior/mid",
            required_seniority="mid",
            is_aligned=True,
            notes=(
                "La seniority sembra abbastanza allineata, anche se alcune competenze "
                "specifiche richieste dalla posizione andrebbero rafforzate."
            ),
        ),
        technical_skills=SkillMatch(
            matched=["Python", "FastAPI", "REST API", ".NET", "C#"],
            missing=["Docker", "PostgreSQL", "CI/CD"],
            extra=["OpenAI API", "Backend development"],
        ),
        soft_skills=SkillMatch(
            matched=["problem solving", "curiosità tecnica", "capacità di apprendimento"],
            missing=["stakeholder management"],
            extra=[],
        ),
        main_gaps=[
            Gap(
                area="DevOps",
                description="L'esperienza con Docker e pipeline CI/CD non è ancora evidente.",
                impact=ImpactLevel.medium,
            ),
            Gap(
                area="Database",
                description="La job description sembra richiedere maggiore familiarità con database relazionali.",
                impact=ImpactLevel.medium,
            ),
        ],
        improvement_suggestions=[
            "Aggiungere al portfolio un progetto FastAPI containerizzato con Docker.",
            "Integrare un database relazionale come PostgreSQL o SQLite.",
            "Scrivere test automatici con pytest per dimostrare attenzione alla qualità.",
        ],
        interview_questions=[
            InterviewQuestion(
                question="Come struttureresti un progetto FastAPI in modo modulare?",
                topic="FastAPI",
                difficulty=DifficultyLevel.medium,
            ),
            InterviewQuestion(
                question="Come gestiresti la validazione dell'output generato da un modello AI?",
                topic="AI integration",
                difficulty=DifficultyLevel.medium,
            ),
            InterviewQuestion(
                question="Qual è la differenza tra un ambiente virtuale Python e l'ambiente globale?",
                topic="Python",
                difficulty=DifficultyLevel.easy,
            ),
        ],
        study_plan=[
            StudyPlanItem(
                topic="FastAPI project structure",
                reason="Serve per costruire API backend pulite e manutenibili.",
                priority=PriorityLevel.high,
                estimated_effort="2-3 days",
            ),
            StudyPlanItem(
                topic="Docker basics",
                reason="Docker è spesso richiesto in contesti enterprise e consulenziali.",
                priority=PriorityLevel.medium,
                estimated_effort="1 week",
            ),
            StudyPlanItem(
                topic="pytest",
                reason="I test rendono il progetto più professionale e presentabile.",
                priority=PriorityLevel.medium,
                estimated_effort="2-3 days",
            ),
        ],
    )