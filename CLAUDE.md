# CLAUDE.md

> Guidance for AI assistants working in the **expert-spork** repository.

## Project Overview

**Expert Spork AI** is a Python-based AI inference platform built by an AI startup in Hurghada,
Egypt. It exposes a FastAPI REST API for model inference with a clean, extensible architecture.

- **Language**: Python 3.11+
- **Framework**: FastAPI + Uvicorn
- **Package layout**: `src/` layout (`src/expert_spork/`)
- **Build system**: Hatch (via `pyproject.toml`)
- **ML backend**: HuggingFace Transformers (optional `[ml]` extra); falls back to a stub

## Repository Structure

```
expert-spork/
├── src/expert_spork/          # Application source code
│   ├── api/                   #   FastAPI route handlers
│   │   └── routes.py          #   /health and /infer endpoints
│   ├── core/                  #   Cross-cutting concerns
│   │   ├── config.py          #   Pydantic Settings (env-driven config)
│   │   └── logging.py         #   structlog setup (JSON or console)
│   ├── ml/                    #   Machine learning layer
│   │   └── engine.py          #   InferenceEngine (load / predict, HF or stub)
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
make install      # Install production dependencies only
make serve        # Start dev server with hot reload (SPORK_DEBUG=true)
make test         # Run pytest
make test-cov     # Run tests with coverage (must pass 80%)
make lint         # Ruff lint check
make format       # Auto-format with ruff + fix auto-fixable issues
make typecheck    # mypy strict mode
make docker-build # Build Docker image
make docker-up    # docker compose up -d
make clean        # Remove build artifacts and cache directories
```

Run `make help` to see all available targets with descriptions.

## Development Setup

```bash
# 1. Clone and set up the environment
git clone <repo-url> && cd expert-spork

# 2. Install dev dependencies and pre-commit hooks
make dev

# 3. Copy and customize environment variables
cp .env.example .env

# 4. Start the dev server
make serve
# → API available at http://localhost:8000
# → Swagger UI at http://localhost:8000/docs
# → Redoc at http://localhost:8000/redoc

# 5. (Optional) Install ML extras for real model inference
pip install -e ".[ml]"
```

## Configuration

All settings use the `SPORK_` prefix, managed via `pydantic-settings` in
`src/expert_spork/core/config.py`. Copy `.env.example` to `.env` for local development.

| Variable               | Default     | Description                          |
|------------------------|-------------|--------------------------------------|
| `SPORK_DEBUG`          | `false`     | Enable debug mode / hot reload       |
| `SPORK_HOST`           | `0.0.0.0`   | Bind address                         |
| `SPORK_PORT`           | `8000`      | Bind port                            |
| `SPORK_WORKERS`        | `1`         | Uvicorn worker count                 |
| `SPORK_MODEL_NAME`     | `default`   | Model identifier (HF model ID or `default`) |
| `SPORK_MODEL_DEVICE`   | `cpu`       | Device (`cpu` or `cuda`)             |
| `SPORK_MAX_BATCH_SIZE` | `32`        | Maximum batch size for inference     |
| `SPORK_LOG_LEVEL`      | `INFO`      | Log level                            |
| `SPORK_LOG_JSON`       | `true`      | Emit JSON-formatted logs (false = console) |

Setting `SPORK_MODEL_NAME` to anything other than `default` (and having the `[ml]` extra
installed) causes the engine to load a real HuggingFace Transformers text-generation pipeline.

## API Reference

All routes are mounted under `/api/v1`.

### `GET /api/v1/health`

Liveness/readiness probe.

**Response** (`200 OK`):
```json
{ "status": "ok", "version": "0.1.0", "model_loaded": true }
```

### `POST /api/v1/infer`

Run inference on input text.

**Request body**:
```json
{
  "text": "Input text (1–10,000 chars)",
  "parameters": { "temperature": 0.7 }   // optional model kwargs
}
```

**Response** (`200 OK`):
```json
{ "result": "...", "model": "default", "tokens_used": 2 }
```

Returns `503` if the model is not loaded; `422` for invalid input.

## Architecture Decisions

- **`src/` layout**: prevents accidental imports from the project root during development
- **Pydantic Settings**: single source of truth for config, fully validated at startup
- **structlog**: structured JSON logging for production observability; switchable to console
- **Lifespan hook** (`main.py`): the `InferenceEngine` is loaded once at startup via
  `asynccontextmanager`, never per-request
- **`asyncio.to_thread`**: CPU-bound HF Transformers inference is offloaded to a thread pool
  via `asyncio.to_thread`, keeping the event loop unblocked
- **HF Transformers / stub fallback**: `InferenceEngine` detects whether `transformers` is
  importable at module load time (`_HAS_TRANSFORMERS`). If absent or `SPORK_MODEL_NAME=default`,
  it returns a stub echo response. No code changes needed to switch between modes.
- **Multi-stage Docker**: builder stage installs deps; runtime stage copies only the installed
  packages, keeping the image lean and free of build tooling

## Testing

- **Framework**: pytest with `pytest-asyncio` (`asyncio_mode = "auto"`)
- **Run**: `make test` or `pytest`
- **Coverage**: `make test-cov` — threshold is **80%** (enforced in CI and in `pyproject.toml`)
- **Markers**:
  - `@pytest.mark.slow` — deselect with `-m "not slow"`
  - `@pytest.mark.integration` — for tests requiring real infrastructure
- **Transport**: tests use `httpx.ASGITransport` to drive FastAPI without a real server
- **Fixtures** (`tests/conftest.py`):
  - `_load_engine` — `autouse=True` fixture that ensures the engine is loaded before every test
  - `client` — `AsyncClient` pre-wired to the app at `http://test`

### Coverage Targets

| Metric           | Target | Enforcement           |
|------------------|--------|-----------------------|
| Line coverage    | ≥ 80%  | `pyproject.toml` + CI |
| Branch coverage  | ≥ 70%  | (aspirational)        |
| Function coverage| ≥ 90%  | (aspirational)        |
| Auth / data mutation | 100% | code review policy |

### Writing New Tests

1. Place tests in `tests/test_<module>.py`
2. Use `async def test_*` functions (asyncio_mode is auto)
3. Inject the `client` fixture for HTTP tests
4. The `_load_engine` autouse fixture handles engine state automatically
5. Add `@pytest.mark.slow` or `@pytest.mark.integration` where appropriate

## Linting & Formatting

- **Linter/Formatter**: Ruff (configured in `pyproject.toml`)
- **Line length**: 99 (soft — E501 is ignored by ruff, but aim to stay under)
- **Import sorting**: isort-compatible via Ruff's `I` rules
- **First-party package**: `expert_spork` (declared in `[tool.ruff.lint.isort]`)
- **Type checking**: mypy in strict mode (`strict = true`)
- **Pre-commit hooks**: ruff format, ruff lint, trailing whitespace, YAML/TOML checks,
  secret detection — all enforced automatically after `make dev`

Always run `make lint` and `make format` before committing. CI will fail on lint or type errors.

## Docker

```bash
# Build image
make docker-build          # → expert-spork:latest

# Run with docker compose
make docker-up             # starts the service via docker-compose.yml

# Manual run
docker run -p 8000:8000 --env-file .env expert-spork
```

The Dockerfile uses a two-stage build:
1. **builder** — installs everything from `pyproject.toml`
2. **runtime** — copies only the installed site-packages and app code; exposes port 8000;
   includes a `HEALTHCHECK` that polls `/api/v1/health`

## CI/CD

GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on push/PR to `main`:

| Job            | Steps                                                    | Blocks merge? |
|----------------|----------------------------------------------------------|---------------|
| `lint`         | `ruff format --check`, `ruff check`, `mypy src/`         | Yes           |
| `test`         | `pytest --cov` on Python 3.11 and 3.12, coverage ≥ 80%  | Yes           |
| `docker`       | `docker build` (needs lint + test to pass first)         | Yes           |

All three jobs must be green before merging to `main`.

## Conventions for AI Assistants

1. **Read before editing** — always read the relevant file(s) before proposing changes
2. **Minimal changes** — do not refactor, add docstrings, or "improve" code beyond what's asked
3. **Run the checks** — after any code change, run `make lint` and `make test` to verify
4. **Follow existing patterns** — match the style of surrounding code; ruff enforces most of it
5. **Type annotations** — all new code must be fully typed (`mypy --strict` is on)
6. **Async by default** — API handlers and engine methods are `async`; keep that invariant
7. **Thread-offload blocking work** — use `asyncio.to_thread()` for CPU-bound or blocking I/O
8. **No secrets in code** — config goes in env vars with the `SPORK_` prefix, never hardcoded
9. **Test new features** — add tests in `tests/` for any new endpoint, module, or behaviour
10. **Pydantic models for I/O** — all API bodies use schemas in `src/expert_spork/schemas/`
11. **Keep the Makefile updated** — add a `make` target for any new developer workflow
12. **Extend the engine cleanly** — swap real model logic (HuggingFace, ONNX, vLLM, etc.)
    into `ml/engine.py` behind the same `load()` / `predict()` interface; do not touch routes

## Dependency Groups

| Extra  | Install command           | Purpose                                    |
|--------|---------------------------|--------------------------------------------|
| (none) | `pip install -e .`        | Runtime only (FastAPI, uvicorn, structlog) |
| `dev`  | `pip install -e ".[dev]"` | Tests, linting, type checking, pre-commit  |
| `ml`   | `pip install -e ".[ml]"`  | Real HF Transformers inference (torch, etc.) |
