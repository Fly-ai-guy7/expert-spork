"""Drug search and EAN-13 barcode lookup."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from db import get_db
from models import Drug
from schemas import DrugOut

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get("", response_model=list[DrugOut])
def search_drugs(
    q: str | None = Query(default=None, description="Free-text search (EN/AR/generic)"),
    category: str | None = None,
    rx: bool | None = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Drug)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Drug.name_en.ilike(like),
                Drug.name_ar.ilike(like),
                Drug.generic.ilike(like),
            )
        )
    if category:
        stmt = stmt.where(Drug.category == category)
    if rx is not None:
        stmt = stmt.where(Drug.rx == rx)
    stmt = stmt.limit(limit)
    return list(db.scalars(stmt))


@router.get("/barcode/{barcode}", response_model=DrugOut)
def lookup_barcode(barcode: str, db: Session = Depends(get_db)):
    drug = db.scalar(select(Drug).where(Drug.barcode == barcode))
    if not drug:
        raise HTTPException(status_code=404, detail="No drug found for barcode")
    return drug


@router.get("/{drug_id}", response_model=DrugOut)
def get_drug(drug_id: int, db: Session = Depends(get_db)):
    drug = db.get(Drug, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug
