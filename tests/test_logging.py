import io
import json
import logging
from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.core.logging_config import JsonFormatter
from app.core.logging_context import reset_request_id, set_request_id
from app.models.match_models import MatchAnalysisRequest
from app.services.match_service import analyze_cv_job_match


SENTINEL_API_KEY = "sk-sentinel-test-key-do-not-log"


def _make_log_record(**extra):
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_produces_valid_json():
    formatter = JsonFormatter()
    token = set_request_id("req-123")

    try:
        output = formatter.format(_make_log_record(event="test_event"))
        parsed = json.loads(output)
    finally:
        reset_request_id(token)

    assert isinstance(parsed, dict)


def test_json_formatter_contains_required_fields():
    formatter = JsonFormatter()
    token = set_request_id("req-456")

    try:
        parsed = json.loads(formatter.format(_make_log_record()))
    finally:
        reset_request_id(token)

    assert "timestamp" in parsed
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test.logger"
    assert parsed["message"] == "Test message"
    assert parsed["request_id"] == "req-456"


def test_json_formatter_includes_supported_extra_fields():
    formatter = JsonFormatter()
    parsed = json.loads(
        formatter.format(
            _make_log_record(
                event="http_request_completed",
                method="GET",
                path="/health",
                status_code=200,
                duration_ms=12.5,
            )
        )
    )

    assert parsed["event"] == "http_request_completed"
    assert parsed["method"] == "GET"
    assert parsed["path"] == "/health"
    assert parsed["status_code"] == 200
    assert parsed["duration_ms"] == 12.5


def test_json_formatter_excludes_non_allowlisted_fields():
    formatter = JsonFormatter()
    parsed = json.loads(
        formatter.format(
            _make_log_record(
                event="test_event",
                secret_payload="must-not-appear",
                api_key=SENTINEL_API_KEY,
            )
        )
    )

    assert parsed["event"] == "test_event"
    assert "secret_payload" not in parsed
    assert "api_key" not in parsed


def test_configure_logging_is_idempotent(monkeypatch):
    import app.core.logging_config as logging_config_module

    monkeypatch.setattr(logging_config_module, "_LOGGING_CONFIGURED", False)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    logging_config_module.configure_logging("INFO")
    handlers_after_first_call = len(root_logger.handlers)

    logging_config_module.configure_logging("DEBUG")
    handlers_after_second_call = len(root_logger.handlers)

    assert handlers_after_first_call == 1
    assert handlers_after_second_call == 1


def test_logs_do_not_contain_sentinel_api_key():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())

    service_logger = logging.getLogger("app.services.match_service")
    openai_logger = logging.getLogger("app.ai.openai_client")
    service_logger.addHandler(handler)
    openai_logger.addHandler(handler)
    service_logger.setLevel(logging.INFO)
    openai_logger.setLevel(logging.INFO)

    original_provider = settings.ai_provider
    original_api_key = settings.openai_api_key

    request = MatchAnalysisRequest(
        cv_text=(
            "Sono uno sviluppatore backend con esperienza in C#, .NET, API REST "
            "e progetti personali in Python. Ho realizzato applicazioni usando "
            "FastAPI e integrazioni con API OpenAI."
        ),
        job_description_text=(
            "Cerchiamo un backend developer con esperienza in Python, FastAPI, "
            "API REST, Docker, database relazionali e integrazione di servizi AI. "
            "Il candidato lavorerà su progetti enterprise."
        ),
        language="it",
    )

    mock_parsed = MagicMock()
    mock_parsed.match_score = 78
    mock_parsed.match_level = MagicMock(value="good")
    mock_content = MagicMock()
    mock_content.parsed = mock_parsed
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_response = MagicMock()
    mock_response.output = [mock_message]

    try:
        settings.ai_provider = "openai"
        settings.openai_api_key = SENTINEL_API_KEY
        stream.truncate(0)
        stream.seek(0)

        with patch("app.ai.openai_client.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_client.responses.parse.return_value = mock_response
            mock_openai_class.return_value = mock_client

            analyze_cv_job_match(request)

        log_output = stream.getvalue()
    finally:
        service_logger.removeHandler(handler)
        openai_logger.removeHandler(handler)
        settings.ai_provider = original_provider
        settings.openai_api_key = original_api_key

    assert SENTINEL_API_KEY not in log_output


def test_match_service_logs_do_not_contain_cv_or_job_description_text():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())

    service_logger = logging.getLogger("app.services.match_service")
    service_logger.addHandler(handler)
    service_logger.setLevel(logging.DEBUG)

    cv_text = (
        "UNIQUE_CV_SENTINEL_PHRASE_XYZ123 sono uno sviluppatore backend con "
        "esperienza in C#, .NET, API REST e progetti personali in Python."
    )
    job_description_text = (
        "UNIQUE_JOB_SENTINEL_PHRASE_ABC789 cerchiamo un backend developer con "
        "esperienza in Python, FastAPI, API REST, Docker e database relazionali."
    )

    try:
        request = MatchAnalysisRequest(
            cv_text=cv_text,
            job_description_text=job_description_text,
            language="it",
        )

        analyze_cv_job_match(request)
        log_output = stream.getvalue()
    finally:
        service_logger.removeHandler(handler)

    assert "UNIQUE_CV_SENTINEL_PHRASE_XYZ123" not in log_output
    assert "UNIQUE_JOB_SENTINEL_PHRASE_ABC789" not in log_output
