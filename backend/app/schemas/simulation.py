import uuid

from pydantic import BaseModel


class SimulationStatus(BaseModel):
    case_id: uuid.UUID
    status: str
    rounds_complete: int
    rounds_total: int
    last_event: str | None = None
    pending_checkpoint_id: uuid.UUID | None = None


class TraineeSubmissionIn(BaseModel):
    content_en: str | None = None
    content_ar: str | None = None
    citations: list[str] = []


class HilActionIn(BaseModel):
    notes: str | None = None
    modified_payload: dict | None = None


class CounselRequestIn(BaseModel):
    content_en: str | None = None
    content_ar: str | None = None
    citations: list[str] = []
