from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.disclaimer import disclaimer_block

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    db_status = "up"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        db_status = f"down: {exc}"
    return {
        "status": "ok",
        "db": db_status,
        "disclaimer": disclaimer_block(),
    }


@router.get("/healthz")
def healthz() -> dict:
    """Liveness: the process is up and serving. No dependency checks — used by
    the orchestrator to decide whether to restart the container."""
    return {"status": "ok"}


@router.get("/readyz")
def readyz(response: Response, db: Session = Depends(get_db)) -> dict:
    """Readiness: dependencies reachable. Returns 503 if not ready so the load
    balancer holds traffic until the instance can actually serve."""
    checks: dict[str, str] = {}
    ready = True

    try:
        db.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as exc:  # pragma: no cover
        checks["db"] = f"down: {exc}"
        ready = False

    if settings.celery_broker_url:
        try:
            import redis

            client = redis.from_url(settings.celery_broker_url, socket_connect_timeout=2)
            client.ping()
            checks["redis"] = "ok"
        except Exception as exc:  # pragma: no cover
            checks["redis"] = f"down: {exc}"
            ready = False
    else:
        checks["redis"] = "eager (no broker)"

    if not ready:
        response.status_code = 503
    return {"status": "ready" if ready else "not_ready", "checks": checks}
