import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.auth.deps import current_user
from app.db import get_db
from app.models import Statute, StatuteArticle, User
from app.schemas.statute import StatuteDetail, StatuteOut

router = APIRouter(prefix="/api/statutes", tags=["statutes"])


@router.get("", response_model=list[StatuteOut])
def list_statutes(
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> list[Statute]:
    return db.execute(select(Statute).order_by(Statute.year.desc())).scalars().all()


@router.get("/search")
def search_articles(
    q: str = Query(min_length=2),
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> list[dict]:
    pattern = f"%{q}%"
    stmt = (
        select(StatuteArticle, Statute)
        .join(Statute)
        .where(or_(StatuteArticle.text_en.ilike(pattern), StatuteArticle.text_ar.ilike(pattern)))
        .limit(50)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "id": str(a.id),
            "short_code": s.short_code,
            "article_number": a.article_number,
            "text_en": a.text_en,
            "text_ar": a.text_ar,
            "title_en": s.title_en,
            "title_ar": s.title_ar,
        }
        for a, s in rows
    ]


@router.get("/{statute_id}", response_model=StatuteDetail)
def get_statute(statute_id: uuid.UUID, db: Session = Depends(get_db)) -> Statute:
    s = db.execute(
        select(Statute).options(selectinload(Statute.articles)).where(Statute.id == statute_id)
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(404, "Statute not found")
    return s
