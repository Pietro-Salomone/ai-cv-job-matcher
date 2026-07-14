from app.ai.prompts import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_match_analysis_prompt,
)
from app.models.match_models import MatchAnalysisRequest


def _sample_request(**overrides) -> MatchAnalysisRequest:
    defaults = {
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
    defaults.update(overrides)
    return MatchAnalysisRequest(**defaults)


def test_build_match_analysis_prompt_includes_cv_text():
    request = _sample_request()
    prompt = build_match_analysis_prompt(request)

    assert request.cv_text in prompt


def test_build_match_analysis_prompt_includes_job_description_text():
    request = _sample_request()
    prompt = build_match_analysis_prompt(request)

    assert request.job_description_text in prompt


def test_build_match_analysis_prompt_includes_requested_language():
    request = _sample_request(language="en")
    prompt = build_match_analysis_prompt(request)

    assert "en" in prompt
    assert "Requested output language" in prompt


def test_build_match_analysis_prompt_uses_all_delimiters():
    request = _sample_request()
    prompt = build_match_analysis_prompt(request)

    assert "<CV>" in prompt
    assert "</CV>" in prompt
    assert "<JOB_DESCRIPTION>" in prompt
    assert "</JOB_DESCRIPTION>" in prompt


def test_system_prompt_contains_injection_protection():
    assert "<CV>" in SYSTEM_PROMPT
    assert "</CV>" in SYSTEM_PROMPT
    assert "<JOB_DESCRIPTION>" in SYSTEM_PROMPT
    assert "</JOB_DESCRIPTION>" in SYSTEM_PROMPT
    assert "untrusted" in SYSTEM_PROMPT.lower()
    assert "ignore" in SYSTEM_PROMPT.lower()


def test_system_prompt_contains_match_level_thresholds():
    prompt_lower = SYSTEM_PROMPT.lower()

    assert "0" in SYSTEM_PROMPT and "39" in SYSTEM_PROMPT and "low" in prompt_lower
    assert "40" in SYSTEM_PROMPT and "59" in SYSTEM_PROMPT and "medium" in prompt_lower
    assert "60" in SYSTEM_PROMPT and "79" in SYSTEM_PROMPT and "good" in prompt_lower
    assert "80" in SYSTEM_PROMPT and "100" in SYSTEM_PROMPT and "excellent" in prompt_lower


def test_system_prompt_forbids_inventing_experience():
    prompt_lower = SYSTEM_PROMPT.lower()

    assert "do not invent" in prompt_lower
    assert "skills" in prompt_lower
    assert "experience" in prompt_lower


def test_prompt_version_is_v2():
    assert PROMPT_VERSION == "v2"
