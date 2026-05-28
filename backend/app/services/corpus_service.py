import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.i18n import Lang, pick
from app.models import Statute, StatuteArticle


def build_statute_block(db: Session, short_codes: list[str] | None, lang: Lang) -> str:
    query = select(Statute).options(selectinload(Statute.articles))
    if short_codes:
        query = query.where(Statute.short_code.in_(short_codes))
    statutes = db.execute(query).scalars().all()

    lines: list[str] = ["EGYPTIAN STATUTE CORPUS (reference only — cite by short_code:article):\n"]
    for s in statutes:
        title = pick(s.title_ar, s.title_en, lang)
        lines.append(f"\n## Law {s.short_code} — {title}")
        for art in sorted(s.articles, key=lambda a: a.article_number):
            text = pick(art.text_ar, art.text_en, lang)
            lines.append(f"\n[{s.short_code} art. {art.article_number}] {text}")
    return "\n".join(lines)


def verify_citations(
    db: Session, refs: list[str]
) -> tuple[list[uuid.UUID], list[str]]:
    """Verify each citation ref against the loaded corpus.

    Returns (valid_article_ids, unverified_refs). A ref is unverified when it
    is malformed (no parseable short_code+article_number) OR the (short_code,
    article_number) pair has no row in `statute_articles`. This is the
    hallucination guardrail — LLMs occasionally cite real-looking law numbers
    with fake article numbers; this surfaces them per-argument.
    """
    valid_ids: list[uuid.UUID] = []
    unverified: list[str] = []
    for raw in refs:
        ref = raw.strip() if isinstance(raw, str) else str(raw).strip()
        if not ref:
            continue
        if ":" in ref:
            short, article_no = ref.split(":", 1)
        elif " art. " in ref:
            short, article_no = ref.split(" art. ", 1)
        else:
            unverified.append(ref)
            continue
        short = short.strip()
        article_no = article_no.strip()
        stmt = (
            select(StatuteArticle.id)
            .join(Statute)
            .where(Statute.short_code == short, StatuteArticle.article_number == article_no)
        )
        row = db.execute(stmt).first()
        if row:
            valid_ids.append(row[0])
        else:
            unverified.append(ref)
    return valid_ids, unverified


def find_articles_by_short_codes(
    db: Session, refs: list[str]
) -> list[uuid.UUID]:
    """Backwards-compatible wrapper that drops unverified refs silently."""
    valid_ids, _ = verify_citations(db, refs)
    return valid_ids
