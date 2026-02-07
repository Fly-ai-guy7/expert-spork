# CLAUDE.md

> Guidance for AI assistants working in the **expert-spork** repository.

## Project Overview

**Expert Spork AI** is a Python-based AI inference platform built by an AI startup in Hurghada, Egypt. It exposes a FastAPI REST API for model inference with a clean, extensible architecture.

- **Language**: Python 3.11+
- **Framework**: FastAPI + Uvicorn
- **Package layout**: `src/` layout (`src/expert_spork/`)
- **Build system**: Hatch (via `pyproject.toml`)

## Repository Structure

```
expert-spork/
├── src/expert_spork/          # Application source code
│   ├── api/                   #   FastAPI route handlers
│   │   └── routes.py          #   /health and /infer endpoints
│   ├── core/                  #   Cross-cutting concerns
│   │   ├── config.py          #   Pydantic Settings (env-driven config)
│   │   └── logging.py         #   structlog setup
│   ├── ml/                    #   Machine learning layer
│   │   └── engine.py          #   InferenceEngine (load / predict)
│   ├── schemas/               #   Pydantic request/response models
│   │   └── inference.py       #   InferenceRequest, InferenceResponse, HealthResponse
│   └── main.py                #   FastAPI app factory, lifespan, CLI entry point
├── tests/                     #   pytest test suite
│   ├── conftest.py            #   Shared fixtures (async client, engine loader)
│   ├── test_config.py         #   Configuration tests
│   ├── test_health.py         #   Health endpoint tests
│   └── test_inference.py      #   Inference endpoint tests
├── .github/workflows/ci.yml   #   GitHub Actions CI pipeline
├── Dockerfile                 #   Multi-stage production image
├── docker-compose.yml         #   Local orchestration
├── Makefile                   #   Developer shortcuts
├── pyproject.toml             #   Dependencies, tool config (ruff, pytest, mypy)
├── .pre-commit-config.yaml    #   Pre-commit hooks
├── .env.example               #   Environment variable template
├── .editorconfig              #   Editor formatting rules
└── .gitignore                 #   Git ignore patterns
```

## Common Commands

```bash
make dev          # Install all deps + pre-commit hooks
make serve        # Start dev server with hot reload
make test         # Run pytest
make test-cov     # Run tests with coverage (must pass 80%)
make lint         # Ruff lint check
make format       # Auto-format with ruff
make typecheck    # mypy strict mode
make docker-build # Build Docker image
make docker-up    # docker compose up -d
make clean        # Remove build artifacts
```

## Testing

- **Framework**: pytest with pytest-asyncio (auto mode)
- **Run**: `make test` or `pytest`
- **Coverage**: `make test-cov` — threshold is **80%** (enforced in CI)
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.integration`
- **Fixtures**: see `tests/conftest.py` — provides `client` (async HTTPX) and auto-loads the engine
- Tests use HTTPX `ASGITransport` to test the FastAPI app without spinning up a real server

## Linting & Formatting

- **Linter/Formatter**: Ruff (configured in `pyproject.toml`)
- **Line length**: 99
- **Import sorting**: isort-compatible via Ruff's `I` rules
- **Type checking**: mypy in strict mode
- **Pre-commit**: runs ruff + format + trailing whitespace + YAML/TOML checks + secret detection

Always run `make lint` and `make format` before committing. Pre-commit hooks enforce this automatically after `make dev`.

## Configuration

All settings are controlled by environment variables with the `SPORK_` prefix. Managed via `pydantic-settings` in `src/expert_spork/core/config.py`.

| Variable                | Default      | Description                    |
|-------------------------|-------------|-------------------------------|
| `SPORK_DEBUG`           | `false`     | Enable debug / hot reload      |
| `SPORK_HOST`            | `0.0.0.0`  | Bind address                   |
| `SPORK_PORT`            | `8000`      | Bind port                      |
| `SPORK_WORKERS`         | `1`         | Uvicorn workers                |
| `SPORK_MODEL_NAME`      | `default`   | Model identifier               |
| `SPORK_MODEL_DEVICE`    | `cpu`       | Device (cpu / cuda)            |
| `SPORK_MAX_BATCH_SIZE`  | `32`        | Max batch size for inference   |
| `SPORK_LOG_LEVEL`       | `INFO`      | Log level                      |
| `SPORK_LOG_JSON`        | `true`      | JSON-formatted logs            |

Copy `.env.example` to `.env` for local development.

## Architecture Decisions

- **src layout**: prevents accidental imports from the project root
- **Pydantic Settings**: single source of truth for all configuration, validated at startup
- **structlog**: structured JSON logging for production observability
- **Lifespan hook**: model is loaded once at startup via `asynccontextmanager`, not per-request
- **InferenceEngine**: singleton in `ml/engine.py` — swap in real model logic (HuggingFace, ONNX, vLLM) behind the same interface
- **Multi-stage Docker**: small production image, build deps don't ship to runtime

## Conventions for AI Assistants

1. **Read before editing** — always read the relevant files before proposing changes
2. **Minimal changes** — do not refactor, add docstrings, or "improve" code beyond what's requested
3. **Run the checks** — after any code change, run `make lint` and `make test` to verify
4. **Follow existing patterns** — match the style of surrounding code (ruff enforces most of this)
5. **Type annotations** — all new code must be fully typed (mypy strict is on)
6. **Async by default** — API handlers and engine methods are async; keep it that way
7. **No secrets in code** — config goes in env vars, never hardcode keys or credentials
8. **Test new features** — add tests in `tests/` for any new endpoint or module
9. **Pydantic models for I/O** — all API request/response bodies use schemas in `schemas/`
10. **Keep the Makefile updated** — if you add a new workflow, add a Make target for it

## CI/CD

GitHub Actions pipeline (`.github/workflows/ci.yml`):
1. **Lint & Typecheck** — ruff format check, ruff lint, mypy
2. **Tests** — pytest with coverage on Python 3.11 and 3.12
3. **Docker build** — validates the image builds successfully

All three jobs must pass before merging to `main`.
