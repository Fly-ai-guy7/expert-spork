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

import payments
from config import get_settings
from db import get_db
from models import Drug, Inventory, Order, OrderItem, OrderStatus, User
from schemas import OrderCreate, OrderOut, RxQueueItem, RxQueueOrder
from security import get_current_user, require_pharmacist

settings = get_settings()
router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def my_orders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """The current user's orders, newest first."""
    return list(
        db.scalars(
            select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
        )
    )


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


def _serialize_queue(order: Order) -> RxQueueOrder:
    """Build a pharmacist-facing view of an order (patient + drug detail)."""
    return RxQueueOrder(
        id=order.id,
        patient_email=order.user.email if order.user else "",
        patient_name=order.user.full_name if order.user else "",
        patient_phone=order.user.phone if order.user else "",
        total_egp=order.total_egp,
        created_at=order.created_at,
        items=[
            RxQueueItem(
                drug_id=item.drug_id,
                name_en=item.drug.name_en if item.drug else "",
                name_ar=item.drug.name_ar if item.drug else "",
                rx=item.drug.rx if item.drug else False,
                quantity=item.quantity,
                unit_price_egp=item.unit_price_egp,
            )
            for item in order.items
        ],
    )


def _queue_for(db: Session, status: OrderStatus) -> list[RxQueueOrder]:
    orders = db.scalars(
        select(Order).where(Order.status == status).order_by(Order.created_at.asc())
    ).all()
    return [_serialize_queue(o) for o in orders]


# NOTE: these literal routes must be declared BEFORE "/{order_id}" so paths like
# "/orders/pending-rx" are not captured by the int order_id parameter.
@router.get("/pending-rx", response_model=list[RxQueueOrder])
def pending_rx_queue(
    _: User = Depends(require_pharmacist),
    db: Session = Depends(get_db),
):
    """Pharmacist queue: orders awaiting Rx verification, oldest first.

    Enriched with patient contact + drug names so the pharmacist can review and
    confirm the prescription. This closes the Rx-gating loop — without it,
    gated orders would never surface to a pharmacist.
    """
    return _queue_for(db, OrderStatus.PENDING_RX_VERIFICATION)


@router.get("/paid", response_model=list[RxQueueOrder])
def paid_queue(
    _: User = Depends(require_pharmacist),
    db: Session = Depends(get_db),
):
    """Fulfillment queue: paid orders awaiting hand-off, oldest first."""
    return _queue_for(db, OrderStatus.PAID)


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


@router.post("/{order_id}/pay")
def pay_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a payment intent for an order awaiting payment.

    Returns a checkout URL (live Paymob) or a `mock` flag (no credentials),
    in which case the client uses `POST /payments/mock/confirm` to settle.
    """
    order = db.get(Order, order_id)
    if not order or (order.user_id != user.id and user.role == "patient"):
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=400,
            detail=f"Order is not payable (status: {order.status.value})",
        )
    intent = payments.create_payment(order, user)
    order.paymob_order_id = intent["reference"]
    db.commit()
    return {"order_id": order.id, "amount_egp": order.total_egp, **intent}


@router.post("/{order_id}/fulfill", response_model=OrderOut)
def fulfill_order(
    order_id: int,
    _: User = Depends(require_pharmacist),
    db: Session = Depends(get_db),
):
    """Pharmacist marks a paid order as fulfilled (handed to the patient)."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="Order is not paid")

    # Decrement stock for items that have an inventory record (clamped at 0).
    # Drugs without an inventory row are left untracked — the catalogue is far
    # larger than what the pharmacy stocks.
    for item in order.items:
        inv = db.scalar(select(Inventory).where(Inventory.drug_id == item.drug_id))
        if inv is not None:
            inv.quantity = max(0, inv.quantity - item.quantity)

    order.status = OrderStatus.FULFILLED
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/reject-rx", response_model=OrderOut)
def reject_rx(
    order_id: int,
    pharmacist: User = Depends(require_pharmacist),
    db: Session = Depends(get_db),
):
    """Pharmacist declines the prescription; the order is cancelled."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING_RX_VERIFICATION:
        raise HTTPException(
            status_code=400, detail="Order is not awaiting Rx verification"
        )
    order.rx_verified_by = pharmacist.email
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order
