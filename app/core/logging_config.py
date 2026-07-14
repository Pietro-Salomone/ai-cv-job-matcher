import json
import logging
import logging.config
import sys
from datetime import datetime, timezone

from app.core.logging_context import get_request_id

VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

STRUCTURED_FIELDS = (
    "event",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "provider",
    "model",
    "match_score",
    "match_level",
    "prompt_version",
    "error_type",
    "cv_length",
    "job_description_length",
    "language",
)

_LOGGING_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }

        for field in STRUCTURED_FIELDS:
            if hasattr(record, field):
                value = getattr(record, field)
                if value is not None:
                    if hasattr(value, "value"):
                        payload[field] = value.value
                    else:
                        payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def _normalize_log_level(log_level: str) -> str:
    normalized = log_level.upper()
    if normalized in VALID_LOG_LEVELS:
        return normalized
    return "INFO"


def configure_logging(log_level: str) -> None:
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    level = _normalize_log_level(log_level)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "app.core.logging_config.JsonFormatter",
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                },
            },
            "root": {
                "level": level,
                "handlers": ["stdout"],
            },
            "loggers": {
                "uvicorn": {
                    "level": level,
                    "handlers": ["stdout"],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": level,
                    "handlers": ["stdout"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": level,
                    "handlers": ["stdout"],
                    "propagate": False,
                },
            },
        }
    )

    _LOGGING_CONFIGURED = True
