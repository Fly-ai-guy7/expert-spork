"""Idempotent statute corpus loader.

Reads /corpus/*.json and upserts into the statutes + statute_articles tables.
Run via: python -m app.corpus_loader
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import Statute, StatuteArticle

logger = logging.getLogger(__name__)


class ArticleFile(BaseModel):
    number: str
    text_ar: str | None = None
    text_en: str | None = None
    tags: list[str] = Field(default_factory=list)


class StatuteFile(BaseModel):
    law_number: int
    year: int
    short_code: str
    title_ar: str | None = None
    title_en: str | None = None
    domain_tags: list[str] = Field(default_factory=list)
    articles: list[ArticleFile] = Field(default_factory=list)


def load_file(db: Session, path: Path) -> tuple[str, int]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = StatuteFile(**raw)

    statute = db.execute(
        select(Statute).where(Statute.law_number == data.law_number, Statute.year == data.year)
    ).scalar_one_or_none()
    if statute is None:
        statute = Statute(
            law_number=data.law_number,
            year=data.year,
            short_code=data.short_code,
            title_ar=data.title_ar,
            title_en=data.title_en,
            domain_tags=data.domain_tags,
        )
        db.add(statute)
        db.flush()
    else:
        statute.short_code = data.short_code
        statute.title_ar = data.title_ar
        statute.title_en = data.title_en
        statute.domain_tags = data.domain_tags

    existing_articles = {a.article_number: a for a in statute.articles}
    upserted = 0
    for art in data.articles:
        if art.number in existing_articles:
            a = existing_articles[art.number]
            a.text_ar = art.text_ar
            a.text_en = art.text_en
            a.tags = art.tags
        else:
            db.add(
                StatuteArticle(
                    statute_id=statute.id,
                    article_number=art.number,
                    text_ar=art.text_ar,
                    text_en=art.text_en,
                    tags=art.tags,
                )
            )
        upserted += 1

    db.commit()
    return data.short_code, upserted


def main() -> int:
    corpus_dir = Path(settings.corpus_dir)
    if not corpus_dir.exists():
        # Fallback for local non-docker runs
        corpus_dir = Path(__file__).resolve().parent.parent.parent / "corpus"
    if not corpus_dir.exists():
        logger.error("Corpus directory not found at %s", corpus_dir)
        return 1

    files = sorted(corpus_dir.glob("*.json"))
    if not files:
        logger.warning("No corpus files found in %s", corpus_dir)
        return 0

    db = SessionLocal()
    try:
        total_articles = 0
        for f in files:
            short_code, count = load_file(db, f)
            logger.info("Loaded %s (%d articles) from %s", short_code, count, f.name)
            total_articles += count
        logger.info("Corpus load complete: %d statutes, %d articles", len(files), total_articles)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    sys.exit(main())
