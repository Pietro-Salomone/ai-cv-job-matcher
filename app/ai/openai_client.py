import logging
import time

from openai import OpenAI, RateLimitError, APIError

from app.ai.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_match_analysis_prompt
from app.core.config import settings
from app.models.match_models import MatchAnalysisRequest, MatchAnalysisResponse
from app.services.exceptions import (
    AIProviderConfigurationError,
    AIProviderError,
    AIProviderQuotaError,
)

logger = logging.getLogger(__name__)


class OpenAIMatchAnalyzer:
    def __init__(self):
        if not settings.openai_api_key:
            raise AIProviderConfigurationError(
                "OPENAI_API_KEY is required when AI_PROVIDER=openai."
            )

        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze(self, request: MatchAnalysisRequest) -> MatchAnalysisResponse:
        model = settings.openai_model
        start = time.perf_counter()

        logger.info(
            "OpenAI request started",
            extra={
                "event": "openai_request_started",
                "provider": "openai",
                "model": model,
                "prompt_version": PROMPT_VERSION,
            },
        )

        try:
            response = self.client.responses.parse(
                model=model,
                instructions=SYSTEM_PROMPT,
                input=build_match_analysis_prompt(request),
                text_format=MatchAnalysisResponse,
            )

            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            logger.info(
                "OpenAI request completed",
                extra={
                    "event": "openai_request_completed",
                    "provider": "openai",
                    "model": model,
                    "duration_ms": duration_ms,
                },
            )

            message = response.output[0]
            content = message.content[0]
            parsed_response = content.parsed

            if parsed_response is None:
                logger.error(
                    "OpenAI response could not be parsed",
                    extra={
                        "event": "openai_response_invalid",
                        "provider": "openai",
                        "model": model,
                    },
                )
                raise AIProviderError(
                    "OpenAI response could not be parsed as MatchAnalysisResponse."
                )

            return parsed_response

        except RateLimitError as exc:
            error_code = None

            if hasattr(exc, "body") and isinstance(exc.body, dict):
                error_code = exc.body.get("code")

            if error_code == "insufficient_quota":
                logger.warning(
                    "OpenAI quota exceeded",
                    extra={
                        "event": "openai_quota_exceeded",
                        "provider": "openai",
                        "model": model,
                    },
                )
                raise AIProviderQuotaError(
                    "OpenAI quota exceeded. Check API billing, credits, or usage limits."
                ) from exc

            logger.warning(
                "OpenAI rate limit reached",
                extra={
                    "event": "openai_rate_limit_reached",
                    "provider": "openai",
                    "model": model,
                },
            )
            raise AIProviderError(
                "OpenAI rate limit reached. Please retry later."
            ) from exc

        except APIError as exc:
            logger.exception(
                "OpenAI API error occurred",
                extra={
                    "event": "openai_api_failed",
                    "provider": "openai",
                    "model": model,
                    "error_type": type(exc).__name__,
                },
            )
            raise AIProviderError(
                "OpenAI API error occurred while generating the analysis."
            ) from exc
