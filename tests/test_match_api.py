from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_match_returns_valid_response():
    payload = {
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

    response = client.post("/api/v1/matches/analyze", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["match_score"] == 78
    assert data["match_level"] == "good"
    assert "candidate_summary" in data
    assert "job_summary" in data
    assert "technical_skills" in data
    assert "main_gaps" in data
    assert "interview_questions" in data
    assert "study_plan" in data


def test_analyze_match_rejects_short_cv_text():
    payload = {
        "cv_text": "too short",
        "job_description_text": (
            "Cerchiamo un backend developer con esperienza in Python, FastAPI, "
            "API REST, Docker, database relazionali e integrazione di servizi AI."
        ),
        "language": "it",
    }

    response = client.post("/api/v1/matches/analyze", json=payload)

    assert response.status_code == 422