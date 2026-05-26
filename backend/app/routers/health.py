from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

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
