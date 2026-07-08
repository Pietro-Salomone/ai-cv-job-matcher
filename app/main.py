from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AI CV / Job Matcher",
    description="API for matching a CV against a job description using AI.",
    version="0.1.0",
)

app.include_router(router)