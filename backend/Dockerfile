# Luxor Guest House API — production image (Cloud Run / Fly / Render-ready).
# Build context is the backend/ directory.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps first for better layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

# App code (FastAPI app + JSON ledger data).
COPY . .

# Cloud Run injects $PORT (default 8080); fall back to 8080 locally.
ENV PORT=8080
EXPOSE 8080

# Shell form so $PORT expands at runtime.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
