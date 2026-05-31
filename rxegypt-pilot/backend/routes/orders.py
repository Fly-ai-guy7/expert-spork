"""Patient orders with Rx drug gating.

LEGAL: Any order containing a prescription-only drug (``Drug.rx == True``) is
placed into ``PENDING_RX_VERIFICATION`` and cannot proceed to payment until a
pharmacist verifies the prescription. The patient is directed to a WhatsApp
confirmation flow with the pharmacy.
"""
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import get_settings
from db import get_db
from models import Drug, Order, OrderItem, OrderStatus, User
from schemas import OrderCreate, OrderOut
from security import get_current_user, require_pharmacist

settings = get_settings()
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order is empty")

    order = Order(user_id=user.id, status=OrderStatus.CART)
    total = 0.0
    requires_rx = False

    for line in payload.items:
        drug = db.get(Drug, line.drug_id)
        if not drug:
            raise HTTPException(
                status_code=404, detail=f"Drug {line.drug_id} not found"
            )
        if drug.rx:
            requires_rx = True
        order.items.append(
            OrderItem(
                drug_id=drug.id,
                quantity=line.quantity,
                unit_price_egp=drug.price_egp,
            )
        )
        total += drug.price_egp * line.quantity

    order.total_egp = round(total, 2)
    order.requires_rx_verification = requires_rx
    order.status = (
        OrderStatus.PENDING_RX_VERIFICATION
        if requires_rx
        else OrderStatus.PENDING_PAYMENT
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)
    if not order or (order.user_id != user.id and user.role == "patient"):
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}/rx-whatsapp")
def rx_whatsapp_link(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a wa.me link for the patient to confirm an Rx order with the pharmacy."""
    order = db.get(Order, order_id)
    if not order or (order.user_id != user.id and user.role == "patient"):
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.requires_rx_verification:
        raise HTTPException(status_code=400, detail="Order has no Rx items")

    msg = (
        f"Experts Pharmacy Hurghada — Rx confirmation\n"
        f"Order #{order.id}\nTotal: EGP {order.total_egp:.2f}\n"
        f"Please confirm my prescription so my order can be prepared."
    )
    phone = settings.pharmacist_whatsapp.lstrip("+")
    return {"whatsapp_url": f"https://wa.me/{phone}?text={quote(msg)}"}


@router.post("/{order_id}/verify-rx", response_model=OrderOut)
def verify_rx(
    order_id: int,
    pharmacist: User = Depends(require_pharmacist),
    db: Session = Depends(get_db),
):
    """Pharmacist confirms the prescription; order moves to PENDING_PAYMENT."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING_RX_VERIFICATION:
        raise HTTPException(
            status_code=400, detail="Order is not awaiting Rx verification"
        )
    order.rx_verified_by = pharmacist.email
    order.status = OrderStatus.PENDING_PAYMENT
    db.commit()
    db.refresh(order)
    return order
