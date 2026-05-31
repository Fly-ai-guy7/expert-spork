"""Stock management — pharmacist-only writes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import Drug, Inventory, User
from schemas import InventoryOut, InventoryUpdate
from security import require_pharmacist

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/low-stock", response_model=list[InventoryOut])
def low_stock(db: Session = Depends(get_db)):
    """Items at or below their reorder level."""
    stmt = select(Inventory).where(Inventory.quantity <= Inventory.reorder_level)
    return list(db.scalars(stmt))


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
    _: User = Depends(require_pharmacist),
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
    db.commit()
    db.refresh(inv)
    return inv
