from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import dashboard_service

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(
    overdue_hours: float = Query(
        default=dashboard_service.OVERDUE_THRESHOLD_HOURS, gt=0
    ),
    recent_limit: int = Query(default=12, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict:
    """v3 case-intelligence dashboard: open issues, overdue items, risk heatmap, recent activity."""
    return dashboard_service.build_dashboard(
        db, overdue_hours=overdue_hours, recent_limit=recent_limit
    )
