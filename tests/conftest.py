import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def force_mock_ai_provider():
    original_ai_provider = settings.ai_provider

    settings.ai_provider = "mock"

    yield

    settings.ai_provider = original_ai_provider