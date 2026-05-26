import uuid

from pydantic import BaseModel, ConfigDict


class StatuteArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    article_number: str
    text_en: str | None
    text_ar: str | None
    tags: list | None


class StatuteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    law_number: int
    year: int
    short_code: str
    title_en: str | None
    title_ar: str | None
    domain_tags: list | None


class StatuteDetail(StatuteOut):
    articles: list[StatuteArticleOut]
