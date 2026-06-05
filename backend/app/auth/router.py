"""Auth endpoints: register, login, me, switch-org."""
from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import refresh as refresh_svc
from app.auth.deps import current_user
from app.auth.security import hash_password, issue_token, verify_password
from app.db import get_db
from app.models import Membership, Organization, Role, User
from app.services import audit

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = None
    organization_name: str = Field(min_length=1, max_length=255)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user_id: uuid.UUID
    org_id: uuid.UUID | None
    role: str | None


class MeOut(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None
    memberships: list[dict]


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")[:64] or "org"


@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    """Self-serve: create a user + a new org + ADMIN membership in one call."""
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
    )
    db.add(user)
    db.flush()

    base_slug = _slugify(payload.organization_name)
    slug = base_slug
    suffix = 1
    while db.execute(select(Organization).where(Organization.slug == slug)).scalar_one_or_none():
        suffix += 1
        slug = f"{base_slug}-{suffix}"

    org = Organization(name=payload.organization_name, slug=slug)
    db.add(org)
    db.flush()

    membership = Membership(user_id=user.id, org_id=org.id, role=Role.ADMIN)
    db.add(membership)
    db.commit()

    audit.record(
        db, action="USER_REGISTER", resource_type="user", resource_id=user.id,
        after={"email": user.email, "org_slug": org.slug}, actor=user, org_id=org.id, request=request,
    )

    access = issue_token(user.id, org.id, Role.ADMIN.value)
    refresh = refresh_svc.issue(db, user_id=user.id, request=request)
    return TokenOut(
        access_token=access, refresh_token=refresh,
        user_id=user.id, org_id=org.id, role=Role.ADMIN.value,
    )


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    user = db.execute(
        select(User).options(selectinload(User.memberships)).where(User.email == payload.email)
    ).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")

    # Default to the first membership; trainee can switch via /switch-org.
    m = user.memberships[0] if user.memberships else None
    org_id = m.org_id if m else None
    role = m.role.value if m else None
    access = issue_token(user.id, org_id, role)
    refresh = refresh_svc.issue(db, user_id=user.id, request=request)
    return TokenOut(
        access_token=access, refresh_token=refresh,
        user_id=user.id, org_id=org_id, role=role,
    )


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(current_user), db: Session = Depends(get_db)) -> MeOut:
    memberships = db.execute(
        select(Membership)
        .options(selectinload(Membership.organization))
        .where(Membership.user_id == user.id)
    ).scalars().all()
    return MeOut(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        memberships=[
            {
                "org_id": str(m.org_id),
                "org_name": m.organization.name,
                "org_slug": m.organization.slug,
                "role": m.role.value,
            }
            for m in memberships
        ],
    )


class SwitchOrgIn(BaseModel):
    org_id: uuid.UUID


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=8, max_length=512)


class LogoutIn(BaseModel):
    refresh_token: str = Field(min_length=8, max_length=512)


@router.post("/refresh", response_model=TokenOut)
def refresh(payload: RefreshIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    """Exchange a refresh token for a new access + rotated refresh. The old
    refresh is revoked; replay of an already-revoked token revokes its
    whole family (theft detection)."""
    try:
        user_id, new_refresh = refresh_svc.exchange(db, raw_token=payload.refresh_token, request=request)
    except refresh_svc.RefreshError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User unavailable")

    m = db.execute(
        select(Membership).where(Membership.user_id == user.id)
    ).scalars().first()
    org_id = m.org_id if m else None
    role = m.role.value if m else None
    access = issue_token(user.id, org_id, role)
    audit.record(
        db, action="REFRESH", resource_type="user", resource_id=user.id,
        actor=user, org_id=org_id, request=request,
    )
    return TokenOut(
        access_token=access, refresh_token=new_refresh,
        user_id=user.id, org_id=org_id, role=role,
    )


@router.post("/logout", status_code=204)
def logout(payload: LogoutIn, request: Request, db: Session = Depends(get_db)) -> None:
    """Revoke the presented refresh token's family. Idempotent — unknown
    tokens return 204 without leaking whether they existed."""
    revoked = refresh_svc.revoke(db, raw_token=payload.refresh_token)
    if revoked:
        audit.record(db, action="LOGOUT", resource_type="user", request=request)


@router.post("/switch-org", response_model=TokenOut)
def switch_org(
    payload: SwitchOrgIn,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> TokenOut:
    m = db.execute(
        select(Membership).where(Membership.user_id == user.id, Membership.org_id == payload.org_id)
    ).scalar_one_or_none()
    if not m:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not a member of that organisation")
    audit.record(
        db, action="SWITCH_ORG", resource_type="organization", resource_id=m.org_id,
        actor=user, org_id=m.org_id, request=request,
    )
    token = issue_token(user.id, m.org_id, m.role.value)
    return TokenOut(access_token=token, user_id=user.id, org_id=m.org_id, role=m.role.value)
