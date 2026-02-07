# Expert Spork AI

AI inference platform built in **Hurghada, Egypt**.

## Quick Start

```bash
# Clone & install
git clone https://github.com/Fly-ai-guy7/expert-spork.git
cd expert-spork
make dev          # installs deps + pre-commit hooks

# Run locally
make serve        # starts uvicorn with hot reload on :8000

# Or via Docker
make docker-build
make docker-up
```

## API

| Method | Endpoint            | Description              |
|--------|---------------------|--------------------------|
| GET    | `/api/v1/health`    | Liveness / readiness     |
| POST   | `/api/v1/infer`     | Run model inference      |

Interactive docs at [localhost:8000/docs](http://localhost:8000/docs) when the server is running.

## Development

```bash
make lint         # ruff linter
make format       # auto-format
make test         # run pytest
make test-cov     # tests + coverage report
make typecheck    # mypy strict mode
```

## Project Layout

```
src/expert_spork/
  api/          # FastAPI routes
  core/         # Config, logging
  ml/           # Model loading & inference engine
  schemas/      # Pydantic request/response models
  main.py       # App factory & entry point
tests/          # pytest suite
```

## Configuration

All settings are read from environment variables prefixed with `SPORK_`.
Copy `.env.example` to `.env` and adjust values. See `src/expert_spork/core/config.py` for the full list.

## License

MIT
