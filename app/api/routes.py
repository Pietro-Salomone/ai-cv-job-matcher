from fastapi import APIRouter

from app.models.match_models import MatchAnalysisRequest, MatchAnalysisResponse
from app.services.match_service import analyze_cv_job_match

router = APIRouter()


@router.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


@router.post(
    "/api/v1/matches/analyze",
    response_model=MatchAnalysisResponse,
    tags=["matches"],
)
def analyze_match(request: MatchAnalysisRequest):
    return analyze_cv_job_match(request)