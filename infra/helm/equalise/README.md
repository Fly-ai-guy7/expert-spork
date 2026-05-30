# EQUALISE Helm chart

Deploys the backend + Celery worker + (optional, dev-only) Redis. Postgres
is assumed to live outside the cluster, wired via `DATABASE_URL` inside
the `existingSecret`.

## Install

```bash
# 1. Build & push images (see docker-compose.prod.yml for the Dockerfile targets)
docker build --target prod -t ghcr.io/your-org/equalise-backend:0.1.0 ./backend
docker push ghcr.io/your-org/equalise-backend:0.1.0

# 2. Create the secret (use sealed-secrets / External Secrets in real life)
kubectl create secret generic equalise-secrets \
  --from-literal=ANTHROPIC_API_KEY=... \
  --from-literal=DEEPSEEK_API_KEY=... \
  --from-literal=JWT_SECRET="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')" \
  --from-literal=DATABASE_URL='postgresql+psycopg://user:pw@managed-pg-host:5432/equalise' \
  --from-literal=CELERY_BROKER_URL='redis://equalise-redis:6379/0' \
  --from-literal=CELERY_RESULT_BACKEND='redis://equalise-redis:6379/1'

# 3. Install
helm upgrade --install equalise infra/helm/equalise \
  --set image.repository=ghcr.io/your-org/equalise-backend \
  --set image.tag=0.1.0
```

## Production guidance

- Set `redis.enabled=false` and point `CELERY_BROKER_URL` at a managed
  Redis (ElastiCache / MemoryStore / Upstash).
- Set `migrations.enabled=true` (default) so `alembic upgrade head` runs
  as a pre-install / pre-upgrade Hook Job — schema is current before
  pods take traffic.
- Tune `backend.hpa` based on real traffic; the orchestrator pipeline is
  CPU-light but `gunicorn -w 4` per pod means each backend replica handles
  4 concurrent request-handlers.
- The worker's `terminationGracePeriodSeconds: 120` gives in-flight
  Celery tasks time to drain on rolling deploy.

## Caveat

This chart is **lint-verified in CI** but not actually deployed in the
current environment. Before going live, render with `helm template`,
review with your platform team, and apply to staging first.
