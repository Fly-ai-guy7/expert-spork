"""JWT auth + PDPL consent endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import Consent, User
from schemas import ConsentIn, ConsentOut, Token, UserOut, UserRegister
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
    if not user or not verify_password(form.password, user.hashed_password):
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
