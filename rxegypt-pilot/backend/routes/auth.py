"""JWT auth + PDPL consent and data-subject-rights endpoints."""
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import Consent, Order, User
from schemas import (
    ConsentIn,
    ConsentOut,
    ConsentStatus,
    DataExport,
    Token,
    UserOut,
    UserRegister,
)
from security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role="patient",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.scalar(select(User).where(User.email == form.username))
    if not user or user.deleted_at is not None or not verify_password(
        form.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(subject=user.email, role=user.role)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/consent", response_model=ConsentOut, status_code=201)
def record_consent(
    payload: ConsentIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record explicit PDPL consent with a server-side timestamp.

    Legal requirement: no health data may be processed until consent is granted.
    """
    consent = Consent(
        user_id=user.id,
        purpose=payload.purpose,
        granted=payload.granted,
        policy_version=payload.policy_version,
        detail=payload.detail,
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


# --- PDPL data-subject rights -------------------------------------------------

def _latest_consent(db: Session, user_id: int) -> Consent | None:
    # Order by id as a tie-breaker: created_at can collide within the same second.
    return db.scalar(
        select(Consent)
        .where(Consent.user_id == user_id)
        .order_by(Consent.created_at.desc(), Consent.id.desc())
        .limit(1)
    )


@router.get("/consent", response_model=ConsentStatus)
def consent_status(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Current consent decision (latest record). `granted=false` if never given."""
    latest = _latest_consent(db, user.id)
    if latest is None:
        return ConsentStatus(granted=False)
    return ConsentStatus(
        granted=latest.granted,
        policy_version=latest.policy_version,
        updated_at=latest.created_at,
    )


@router.post("/consent/withdraw", response_model=ConsentOut, status_code=201)
def withdraw_consent(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Withdraw consent (PDPL). Logs a new, timestamped `granted=False` record."""
    consent = Consent(
        user_id=user.id,
        purpose="health_data_processing",
        granted=False,
        policy_version="1.0",
        detail="Consent withdrawn by data subject.",
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


@router.get("/export", response_model=DataExport)
def export_my_data(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """PDPL data portability: everything held about the current user."""
    consents = list(
        db.scalars(
            select(Consent).where(Consent.user_id == user.id).order_by(Consent.created_at)
        )
    )
    orders = list(
        db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.created_at))
    )
    return DataExport(user=user, consents=consents, orders=orders)


@router.delete("/account", status_code=200)
def delete_my_account(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """PDPL erasure: anonymize the account and deactivate it.

    Identifying fields are scrubbed and login is blocked. De-identified order
    records are retained (Egyptian pharmacy/tax retention) — they no longer link
    to any personal data beyond an opaque user id.
    """
    if user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Account already deleted")

    # Log the erasure as a consent withdrawal for the audit trail.
    db.add(Consent(
        user_id=user.id, purpose="account_erasure", granted=False,
        policy_version="1.0", detail="Account erased by data subject (PDPL).",
    ))

    user.email = f"deleted+{user.id}@rxegypt.invalid"
    user.full_name = ""
    user.phone = ""
    user.hashed_password = hash_password(secrets.token_urlsafe(32))  # unusable
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "Account deleted and personal data anonymized.", "user_id": user.id}
