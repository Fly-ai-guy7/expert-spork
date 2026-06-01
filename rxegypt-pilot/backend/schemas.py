"""Pydantic request/response schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models import OrderStatus


class DrugOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name_en: str
    name_ar: str
    generic: str
    form: str
    strength: str
    category: str
    manufacturer: str
    barcode: str
    price_egp: float
    rx: bool
    rx_source: str


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    drug_id: int
    quantity: int
    reorder_level: int
    updated_at: datetime


class InventoryUpdate(BaseModel):
    quantity: int = Field(ge=0)
    reorder_level: int | None = Field(default=None, ge=0)


# --- Auth ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = ""
    phone: str = ""


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    phone: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Consent (PDPL) ---
class ConsentIn(BaseModel):
    purpose: str = "health_data_processing"
    granted: bool
    policy_version: str = "1.0"
    detail: str = ""


class ConsentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    purpose: str
    granted: bool
    policy_version: str
    created_at: datetime


class ConsentStatus(BaseModel):
    """Latest consent decision for the current user (PDPL transparency)."""

    granted: bool          # False if never granted or withdrawn
    policy_version: str | None = None
    updated_at: datetime | None = None


# --- Orders ---
class OrderItemIn(BaseModel):
    drug_id: int
    quantity: int = Field(ge=1)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    drug_id: int
    quantity: int
    unit_price_egp: float


class OrderCreate(BaseModel):
    items: list[OrderItemIn]


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatus
    requires_rx_verification: bool
    rx_verified_by: str
    total_egp: float
    items: list[OrderItemOut]
    created_at: datetime


class RxQueueItem(BaseModel):
    """An item line enriched with the drug name, for the pharmacist queue."""

    drug_id: int
    name_en: str
    name_ar: str
    rx: bool
    quantity: int
    unit_price_egp: float


class RxQueueOrder(BaseModel):
    """An order awaiting Rx verification, with patient + drug detail for the queue."""

    id: int
    patient_email: str
    patient_name: str
    patient_phone: str
    total_egp: float
    created_at: datetime
    items: list[RxQueueItem]


class DataExport(BaseModel):
    """PDPL data-portability export of everything tied to the user."""

    user: UserOut
    consents: list[ConsentOut]
    orders: list[OrderOut]


class MockPayment(BaseModel):
    """Simulated gateway result, used only when payments run in MOCK mode."""

    order_id: int
    success: bool = True
