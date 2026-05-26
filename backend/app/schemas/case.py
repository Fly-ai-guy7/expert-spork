import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import CaseSource, CaseStatus, EvidenceKind, PartyKind, PartyRole


class PartyIn(BaseModel):
    role: PartyRole
    kind: PartyKind = PartyKind.NATURAL
    name_en: str | None = None
    name_ar: str | None = None


class PartyOut(PartyIn):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class FactIn(BaseModel):
    text_en: str | None = None
    text_ar: str | None = None
    disputed: bool = False
    order_index: int = 0


class FactOut(FactIn):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class EvidenceIn(BaseModel):
    kind: EvidenceKind = EvidenceKind.DOCUMENT
    title_en: str | None = None
    title_ar: str | None = None
    description: str | None = None
    missing: bool = False


class EvidenceOut(EvidenceIn):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class CaseIn(BaseModel):
    title_en: str | None = None
    title_ar: str | None = None
    summary_en: str | None = None
    summary_ar: str | None = None
    language_primary: str = "en"
    jurisdiction: str = "EG"
    area_of_law: str | None = None
    created_by: str | None = None
    parties: list[PartyIn] = Field(default_factory=list)
    facts: list[FactIn] = Field(default_factory=list)
    evidence: list[EvidenceIn] = Field(default_factory=list)
    statutes: list[str] = Field(default_factory=list)


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title_en: str | None
    title_ar: str | None
    summary_en: str | None
    summary_ar: str | None
    language_primary: str
    jurisdiction: str
    status: CaseStatus
    source: CaseSource
    difficulty: int | None
    area_of_law: str | None
    created_at: datetime
    parties: list[PartyOut]
    facts: list[FactOut]
    evidence: list[EvidenceOut]


class CaseListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title_en: str | None
    title_ar: str | None
    status: CaseStatus
    source: CaseSource
    area_of_law: str | None
    difficulty: int | None
    created_at: datetime


class GenerateCaseIn(BaseModel):
    area_of_law: str = "IP"
    difficulty: int = Field(default=2, ge=1, le=5)
    language: str = "en"
    user_id: str | None = None


class RunIn(BaseModel):
    max_rounds: int | None = None


class StartTrainingIn(BaseModel):
    trainee_role: str = "DEFENSE"  # PROSECUTION | DEFENSE
    user_id: str = "anonymous"
    difficulty: int = 2
