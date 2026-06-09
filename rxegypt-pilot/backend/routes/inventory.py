"""Stock management — pharmacist-only writes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import audit
from db import get_db
from models import Drug, Inventory, User
from schemas import InventoryOut, InventoryUpdate, LowStockItem
from security import require_pharmacist

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/low-stock", response_model=list[LowStockItem])
def low_stock(db: Session = Depends(get_db)):
    """Items at or below their reorder level, with drug names for reordering."""
    stmt = (
        select(Inventory, Drug)
        .join(Drug, Drug.id == Inventory.drug_id)
        .where(Inventory.quantity <= Inventory.reorder_level)
        .order_by(Inventory.quantity.asc())
    )
    return [
        LowStockItem(
            drug_id=inv.drug_id,
            name_en=drug.name_en,
            name_ar=drug.name_ar,
            quantity=inv.quantity,
            reorder_level=inv.reorder_level,
        )
        for inv, drug in db.execute(stmt).all()
    ]


@router.get("/{drug_id}", response_model=InventoryOut)
def get_inventory(drug_id: int, db: Session = Depends(get_db)):
    inv = db.scalar(select(Inventory).where(Inventory.drug_id == drug_id))
    if not inv:
        raise HTTPException(status_code=404, detail="No inventory record")
    return inv


@router.put("/{drug_id}", response_model=InventoryOut)
def update_inventory(
    drug_id: int,
    payload: InventoryUpdate,
    db: Session = Depends(get_db),
    pharmacist: User = Depends(require_pharmacist),
):
    if not db.get(Drug, drug_id):
        raise HTTPException(status_code=404, detail="Drug not found")
    inv = db.scalar(select(Inventory).where(Inventory.drug_id == drug_id))
    if not inv:
        inv = Inventory(drug_id=drug_id, quantity=0)
        db.add(inv)
    inv.quantity = payload.quantity
    if payload.reorder_level is not None:
        inv.reorder_level = payload.reorder_level
    audit.record(db, pharmacist.email, "inventory_set", f"drug:{drug_id}",
                 detail=f"qty={payload.quantity}")
    db.commit()
    db.refresh(inv)
    return inv
