# AI CV / Job Matcher

![CI](https://github.com/Pietro-Salomone/ai-cv-job-matcher/actions/workflows/ci.yml/badge.svg)

AI CV / Job Matcher is a Python backend API that compares a candidate CV with a job description and returns a structured analysis of the match.
The project is built with FastAPI, Pydantic and OpenAI API integration.

## Features

- Analyze a CV against a job description
- Generate a matching score from 0 to 100
- Extract matched and missing technical skills
- Extract matched and missing soft skills
- Estimate seniority alignment
- Identify main gaps between the CV and the role
- Suggest improvement areas
- Generate technical interview questions
- Generate a personalized study plan
- Return validated JSON responses using Pydantic
- Support mock mode for local development and testing
- Support OpenAI mode for real AI-generated analysis

## Tech Stack

- Python
- FastAPI
- Pydantic
- OpenAI API
- Uvicorn
- pytest
- python-dotenv
- pydantic-settings

## Project Structure

```text
ai-cv-job-matcher/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   └── prompts.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   └── logging_context.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── request_logging.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── match_models.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── exceptions.py
│       └── match_service.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_match_api.py
│   └── test_match_api_errors.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai-cv-job-matcher
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it.

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file starting from `.env.example`.

```env
AI_PROVIDER=mock
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
```

Available providers:

```text
mock
openai
```

Use `mock` for local development and automated tests.

Use `openai` to call the OpenAI API.

Example:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Do not commit your `.env` file.

The `.env` file is intended for local development only. In production, inject
configuration and secrets through your platform's secret manager or runtime
environment variables. Do not bake secrets into Docker images.

## Docker

### Prerequisites

- Docker Engine with Compose support
- No `.env` file is required to start in mock mode

### Build and run with Docker

Build the image:

```bash
docker build -t ai-cv-job-matcher:local .
```

Run in mock mode:

```bash
docker run --rm -p 8000:8000 -e AI_PROVIDER=mock ai-cv-job-matcher:local
```

Run with OpenAI at runtime (provide the API key via environment, never in the image):

```bash
docker run --rm -p 8000:8000 \
  -e AI_PROVIDER=openai \
  -e OPENAI_API_KEY=your_api_key_here \
  ai-cv-job-matcher:local
```

### Run with Docker Compose

Start the API:

```bash
docker compose up --build
```

Stop the stack:

```bash
docker compose down
```

View logs:

```bash
docker compose logs api
```

Compose defaults to `AI_PROVIDER=mock` when no `.env` file is present. To use
OpenAI, set `AI_PROVIDER=openai` and `OPENAI_API_KEY` in your shell or a local
`.env` file used only at runtime by Compose.

### Endpoints

- Health check: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs

The container runs as a non-root user, exposes port `8000`, and writes structured
JSON logs to stdout.

## Continuous Integration

GitHub Actions runs the CI workflow on:

- push to `main`;
- pull requests targeting `main`;
- manual trigger via `workflow_dispatch`.

The pipeline has two jobs:

1. **Python tests** — installs dependencies on Python 3.13, sets
   `AI_PROVIDER=mock`, and runs `python -m pytest -v`. No OpenAI API key is
   required and no call to OpenAI is made.
2. **Docker build and smoke test** — runs only after tests pass. Builds the
   Docker image, verifies the container runs as a non-root user, starts the
   container in mock mode, and checks `GET /health` with retries.

The CI pipeline does not publish Docker images, does not deploy, and does not
use repository secrets.

Workflow file: `.github/workflows/ci.yml`

## Run the API

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Analyze CV / Job Match

```http
POST /api/v1/matches/analyze
```

Example request:

```json
{
  "cv_text": "Sono uno sviluppatore backend con esperienza in C#, .NET, API REST e progetti personali in Python. Ho realizzato applicazioni usando FastAPI e integrazioni con API OpenAI.",
  "job_description_text": "Cerchiamo un backend developer con esperienza in Python, FastAPI, API REST, Docker, database relazionali e integrazione di servizi AI. Il candidato lavorerà su progetti enterprise.",
  "language": "it"
}
```

Example response:

```json
{
  "match_score": 78,
  "match_level": "good",
  "candidate_summary": "Il candidato mostra un background tecnico solido, con esperienza nello sviluppo backend e interesse verso Python, FastAPI e AI generativa.",
  "job_summary": "La posizione richiede competenze backend, capacità di lavorare con API, conoscenza di strumenti AI e familiarità con architetture moderne.",
  "seniority_match": {
    "candidate_seniority": "junior/mid",
    "required_seniority": "mid",
    "is_aligned": true,
    "notes": "La seniority sembra abbastanza allineata, anche se alcune competenze specifiche richieste dalla posizione andrebbero rafforzate."
  },
  "technical_skills": {
    "matched": ["Python", "FastAPI", "REST API", ".NET", "C#"],
    "missing": ["Docker", "PostgreSQL", "CI/CD"],
    "extra": ["OpenAI API", "Backend development"]
  },
  "soft_skills": {
    "matched": ["problem solving", "curiosità tecnica", "capacità di apprendimento"],
    "missing": ["stakeholder management"],
    "extra": []
  },
  "main_gaps": [
    {
      "area": "DevOps",
      "description": "L'esperienza con Docker e pipeline CI/CD non è ancora evidente.",
      "impact": "medium"
    },
    {
      "area": "Database",
      "description": "La job description sembra richiedere maggiore familiarità con database relazionali.",
      "impact": "medium"
    }
  ],
  "improvement_suggestions": [
    "Aggiungere al portfolio un progetto FastAPI containerizzato con Docker.",
    "Integrare un database relazionale come PostgreSQL o SQLite.",
    "Scrivere test automatici con pytest per dimostrare attenzione alla qualità."
  ],
  "interview_questions": [
    {
      "question": "Come struttureresti un progetto FastAPI in modo modulare?",
      "topic": "FastAPI",
      "difficulty": "medium"
    },
    {
      "question": "Come gestiresti la validazione dell'output generato da un modello AI?",
      "topic": "AI integration",
      "difficulty": "medium"
    },
    {
      "question": "Qual è la differenza tra un ambiente virtuale Python e l'ambiente globale?",
      "topic": "Python",
      "difficulty": "easy"
    }
  ],
  "study_plan": [
    {
      "topic": "FastAPI project structure",
      "reason": "Serve per costruire API backend pulite e manutenibili.",
      "priority": "high",
      "estimated_effort": "2-3 days"
    },
    {
      "topic": "Docker basics",
      "reason": "Docker è spesso richiesto in contesti enterprise e consulenziali.",
      "priority": "medium",
      "estimated_effort": "1 week"
    },
    {
      "topic": "pytest",
      "reason": "I test rendono il progetto più professionale e presentabile.",
      "priority": "medium",
      "estimated_effort": "2-3 days"
    }
  ]
}
```

## Running Tests

```bash
pytest -v
```

The test suite covers:

- health check endpoint
- successful match analysis response
- request validation
- AI provider quota error handling
- AI provider configuration error handling
- generic AI provider error handling

## Error Handling

The API converts AI provider errors into clear HTTP responses.

| Error | HTTP Status |
|---|---|
| AI provider quota exceeded | 503 Service Unavailable |
| AI provider not configured | 500 Internal Server Error |
| Generic AI provider error | 502 Bad Gateway |
| Invalid request body | 422 Unprocessable Entity |

## Development Modes

The project supports two AI modes.

### Mock Mode

Used for local development and tests.

```env
AI_PROVIDER=mock
```

This mode returns a deterministic mocked response.

### OpenAI Mode

Used for real AI-generated analysis.

```env
AI_PROVIDER=openai
```

This mode requires a valid OpenAI API key and available API quota.

## Main Design Choices

### Stateless API

The first version does not use a database. Each request contains the CV text and the job description text, and the API returns the analysis immediately.

This keeps the MVP simple, easy to test and easy to run locally.

### Pydantic Validation

The API uses Pydantic models for both request and response validation.

This is especially important when integrating generative AI, because the system should not blindly trust unstructured model output.

### Mock Provider

The mock provider allows the API and the tests to work without external dependencies, network calls or API costs.

### OpenAI Provider

The OpenAI provider is isolated in the `app/ai` layer. This keeps the AI integration separate from the FastAPI routes and application logic.

## Roadmap

- [x] FastAPI project setup
- [x] Pydantic request/response models
- [x] Mock match analysis endpoint
- [x] OpenAI integration
- [x] Error handling
- [x] API tests
- [x] Improve prompt quality
- [x] Add structured logging
- [x] Add Docker support
- [x] Add GitHub Actions CI
- [ ] Add optional persistence layer
- [ ] Add simple frontend or demo UI

## Useful Commands

Run the API:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -v
```

Check tracked files:

```bash
git status
```

## Notes

This project is intended for learning.

It focuses on building a realistic backend API with clean structure, validated data contracts, AI integration and testable behavior.
