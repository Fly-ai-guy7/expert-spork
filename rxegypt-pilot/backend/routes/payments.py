"""Payment settlement endpoints — Paymob callback (live) + mock confirm (test)."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

import payments
from db import get_db
from models import Order, OrderStatus, User
from schemas import MockPayment, OrderOut
from security import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/mock/confirm", response_model=OrderOut)
def mock_confirm(
    payload: MockPayment,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Settle a payment in MOCK mode (no Paymob credentials configured).

    Stands in for the gateway callback so the lifecycle is testable. Disabled
    when live Paymob credentials are present.
    """
    if payments.is_live():
        raise HTTPException(status_code=404, detail="Not available in live mode")

    order = db.get(Order, payload.order_id)
    if not order or (order.user_id != user.id and user.role == "patient"):
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=400,
            detail=f"Order is not awaiting payment (status: {order.status.value})",
        )
    if payload.success:
        order.status = OrderStatus.PAID
        db.commit()
        db.refresh(order)
    return order


@router.post("/paymob/callback")
async def paymob_callback(request: Request, db: Session = Depends(get_db)):
    """Paymob processed-transaction callback (LIVE). HMAC-verified.

    Marks the referenced order PAID on a successful transaction. Paymob also
    calls a separate redirection URL for the user's browser; this is the
    server-to-server notification that is the source of truth.
    """
    if not payments.is_live():
        raise HTTPException(status_code=404, detail="Not available in mock mode")

    body = await request.json()
    obj = body.get("obj", body)
    received_hmac = request.query_params.get("hmac", "")
    if not payments.verify_callback_hmac(obj, received_hmac):
        raise HTTPException(status_code=400, detail="Invalid HMAC")

    pm_order = obj.get("order", {}) or {}
    merchant_order_id = pm_order.get("merchant_order_id")
    order = None
    if merchant_order_id:
        order = db.get(Order, int(merchant_order_id))
    if order is None:  # fall back to the stored Paymob order id
        order = db.scalar(
            select(Order).where(Order.paymob_order_id == str(pm_order.get("id")))
        )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if obj.get("success") and order.status == OrderStatus.PENDING_PAYMENT:
        order.status = OrderStatus.PAID
        db.commit()
    return {"received": True, "order_id": order.id, "status": order.status.value}
