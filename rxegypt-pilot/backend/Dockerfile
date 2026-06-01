# RxEgypt backend — FastAPI (production image).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps first for better layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

# App code (includes Alembic migrations + the gzipped drug seed).
COPY . .

EXPOSE 8000

# Migrations + seeding are run via the platform release step (fly.toml
# release_command / docker-compose command), not here, so the container stays a
# single-purpose web process.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
