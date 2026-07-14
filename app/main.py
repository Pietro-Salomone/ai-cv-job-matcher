from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware

configure_logging(settings.log_level)

app = FastAPI(
    title="AI CV / Job Matcher",
    description="API for matching a CV against a job description using AI.",
    version="0.1.0",
)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(router)
