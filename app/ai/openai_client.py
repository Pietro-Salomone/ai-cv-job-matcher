from openai import OpenAI, RateLimitError, APIError

from app.ai.prompts import SYSTEM_PROMPT, build_match_analysis_prompt
from app.core.config import settings
from app.models.match_models import MatchAnalysisRequest, MatchAnalysisResponse
from app.services.exceptions import (
    AIProviderConfigurationError,
    AIProviderError,
    AIProviderQuotaError,
)


class OpenAIMatchAnalyzer:
    def __init__(self):
        if not settings.openai_api_key:
            raise AIProviderConfigurationError(
                "OPENAI_API_KEY is required when AI_PROVIDER=openai."
            )

        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze(self, request: MatchAnalysisRequest) -> MatchAnalysisResponse:
        try:
            response = self.client.responses.parse(
                model=settings.openai_model,
                instructions=SYSTEM_PROMPT,
                input=build_match_analysis_prompt(request),
                text_format=MatchAnalysisResponse,
            )

            message = response.output[0]
            content = message.content[0]
            parsed_response = content.parsed

            if parsed_response is None:
                raise AIProviderError(
                    "OpenAI response could not be parsed as MatchAnalysisResponse."
                )

            return parsed_response

        except RateLimitError as exc:
            error_code = None

            if hasattr(exc, "body") and isinstance(exc.body, dict):
                error_code = exc.body.get("code")

            if error_code == "insufficient_quota":
                raise AIProviderQuotaError(
                    "OpenAI quota exceeded. Check API billing, credits, or usage limits."
                ) from exc

            raise AIProviderError(
                "OpenAI rate limit reached. Please retry later."
            ) from exc

        except APIError as exc:
            raise AIProviderError(
                "OpenAI API error occurred while generating the analysis."
            ) from exc