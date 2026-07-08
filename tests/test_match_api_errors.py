from fastapi.testclient import TestClient

import app.api.routes as routes_module
from app.main import app
from app.services.exceptions import (
    AIProviderConfigurationError,
    AIProviderError,
    AIProviderQuotaError,
)


client = TestClient(app)


def _valid_payload():
    return {
        "cv_text": (
            "Sono uno sviluppatore backend con esperienza in C#, .NET, API REST "
            "e progetti personali in Python. Ho realizzato applicazioni usando "
            "FastAPI e integrazioni con API OpenAI."
        ),
        "job_description_text": (
            "Cerchiamo un backend developer con esperienza in Python, FastAPI, "
            "API REST, Docker, database relazionali e integrazione di servizi AI. "
            "Il candidato lavorerà su progetti enterprise."
        ),
        "language": "it",
    }


def test_analyze_match_returns_503_when_ai_quota_is_exceeded(monkeypatch):
    def fake_analyze_cv_job_match(request):
        raise AIProviderQuotaError(
            "OpenAI quota exceeded. Check API billing, credits, or usage limits."
        )

    monkeypatch.setattr(
        routes_module,
        "analyze_cv_job_match",
        fake_analyze_cv_job_match,
    )

    response = client.post("/api/v1/matches/analyze", json=_valid_payload())

    assert response.status_code == 503
    assert response.json() == {
        "detail": "OpenAI quota exceeded. Check API billing, credits, or usage limits."
    }


def test_analyze_match_returns_500_when_ai_provider_is_not_configured(monkeypatch):
    def fake_analyze_cv_job_match(request):
        raise AIProviderConfigurationError(
            "OPENAI_API_KEY is required when AI_PROVIDER=openai."
        )

    monkeypatch.setattr(
        routes_module,
        "analyze_cv_job_match",
        fake_analyze_cv_job_match,
    )

    response = client.post("/api/v1/matches/analyze", json=_valid_payload())

    assert response.status_code == 500
    assert response.json() == {
        "detail": "OPENAI_API_KEY is required when AI_PROVIDER=openai."
    }


def test_analyze_match_returns_502_when_ai_provider_fails(monkeypatch):
    def fake_analyze_cv_job_match(request):
        raise AIProviderError(
            "OpenAI API error occurred while generating the analysis."
        )

    monkeypatch.setattr(
        routes_module,
        "analyze_cv_job_match",
        fake_analyze_cv_job_match,
    )

    response = client.post("/api/v1/matches/analyze", json=_valid_payload())

    assert response.status_code == 502
    assert response.json() == {
        "detail": "OpenAI API error occurred while generating the analysis."
    }