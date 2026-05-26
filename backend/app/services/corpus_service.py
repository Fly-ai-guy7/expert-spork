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


def find_articles_by_short_codes(
    db: Session, refs: list[str]
) -> list[uuid.UUID]:
    """Resolve mixed refs like '82/2002:1' or '82/2002 art. 1' to article UUIDs."""
    ids: list[uuid.UUID] = []
    for ref in refs:
        ref = ref.strip()
        if ":" in ref:
            short, article_no = ref.split(":", 1)
        elif " art. " in ref:
            short, article_no = ref.split(" art. ", 1)
        else:
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
            ids.append(row[0])
    return ids
