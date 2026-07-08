from fastapi import APIRouter, HTTPException, status

from app.models.match_models import MatchAnalysisRequest, MatchAnalysisResponse
from app.services.exceptions import (
    AIProviderConfigurationError,
    AIProviderError,
    AIProviderQuotaError,
)
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
    try:
        return analyze_cv_job_match(request)

    except AIProviderQuotaError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except AIProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc