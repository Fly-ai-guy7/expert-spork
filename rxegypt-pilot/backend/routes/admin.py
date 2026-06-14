"""Admin oversight metrics."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db import get_db
from models import Inventory, Order, User
from security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics")
def metrics(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Headline numbers for the admin dashboard."""
    by_status = dict(
        db.execute(select(Order.status, func.count()).group_by(Order.status)).all()
    )
    orders_by_status = {status.value: count for status, count in by_status.items()}

    total_patients = db.scalar(
        select(func.count()).select_from(User)
        .where(User.role == "patient", User.deleted_at.is_(None))
    )
    low_stock = db.scalar(
        select(func.count()).select_from(Inventory)
        .where(Inventory.quantity <= Inventory.reorder_level)
    )
    return {
        "orders_by_status": orders_by_status,
        "total_orders": sum(orders_by_status.values()),
        "active_patients": total_patients or 0,
        "low_stock_items": low_stock or 0,
    }
