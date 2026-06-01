"""SQLAlchemy models for RxEgypt Pilot.

Design notes
------------
* ``Drug.rx`` flags prescription-only medicines. Orders containing any rx drug
  cannot be fulfilled without pharmacist verification (see ``orders.py``) — this
  is a legal requirement under Egyptian pharmacy regulation.
* ``Consent`` records explicit PDPL (Law 151/2020) consent with a timestamp
  before any health data is processed.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class OrderStatus(str, Enum):
    CART = "cart"
    PENDING_RX_VERIFICATION = "pending_rx_verification"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class Drug(Base):
    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_en: Mapped[str] = mapped_column(String(255), index=True)
    name_ar: Mapped[str] = mapped_column(String(255), index=True)
    generic: Mapped[str] = mapped_column(String(255), index=True, default="")
    form: Mapped[str] = mapped_column(String(64), default="")  # tablet, syrup...
    strength: Mapped[str] = mapped_column(String(64), default="")
    category: Mapped[str] = mapped_column(String(128), default="", index=True)
    manufacturer: Mapped[str] = mapped_column(String(255), default="")
    barcode: Mapped[str] = mapped_column(String(32), index=True, default="")  # EAN-13
    price_egp: Mapped[float] = mapped_column(Float, default=0.0)
    rx: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # Provenance of the rx flag (e.g. "manual", or the dataset + "(heuristic)").
    # Heuristic values must be reconciled against the EDA register before go-live.
    rx_source: Mapped[str] = mapped_column(String(255), default="manual")

    inventory: Mapped["Inventory"] = relationship(
        back_populates="drug", uselist=False, cascade="all, delete-orphan"
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_id: Mapped[int] = mapped_column(
        ForeignKey("drugs.id", ondelete="CASCADE"), unique=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=10)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    drug: Mapped["Drug"] = relationship(back_populates="inventory")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="patient")  # patient|pharmacist|admin
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # PDPL erasure: when set, the account is anonymized + deactivated (login and
    # existing tokens are rejected). De-identified order records are retained.
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    consents: Mapped[list["Consent"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus), default=OrderStatus.CART
    )
    requires_rx_verification: Mapped[bool] = mapped_column(Boolean, default=False)
    rx_verified_by: Mapped[str] = mapped_column(String(255), default="")
    total_egp: Mapped[float] = mapped_column(Float, default=0.0)
    paymob_order_id: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    drug_id: Mapped[int] = mapped_column(ForeignKey("drugs.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price_egp: Mapped[float] = mapped_column(Float, default=0.0)

    order: Mapped["Order"] = relationship(back_populates="items")
    drug: Mapped["Drug"] = relationship()


class Consent(Base):
    """PDPL (Law 151/2020) explicit consent record for health-data processing."""

    __tablename__ = "consents"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    purpose: Mapped[str] = mapped_column(String(128), default="health_data_processing")
    granted: Mapped[bool] = mapped_column(Boolean, default=False)
    policy_version: Mapped[str] = mapped_column(String(32), default="1.0")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="consents")
