from openai import OpenAI

from app.ai.prompts import SYSTEM_PROMPT, build_match_analysis_prompt
from app.core.config import settings
from app.models.match_models import MatchAnalysisRequest, MatchAnalysisResponse


class OpenAIMatchAnalyzer:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai.")

        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze(self, request: MatchAnalysisRequest) -> MatchAnalysisResponse:
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
            raise ValueError("OpenAI response could not be parsed as MatchAnalysisResponse.")

        return parsed_response