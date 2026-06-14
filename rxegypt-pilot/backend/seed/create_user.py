"""Create or update a RxEgypt user account.

`/auth/register` only ever creates **patient** accounts, so this CLI is the way
to provision a **pharmacist** (or admin) account — needed to sign in to the POS
(``frontend/pharmacy-pos.html``).

Usage (from the ``backend/`` directory)::

    python seed/create_user.py --email pharmacist@experts.eg --password secret123 \
        --role pharmacist --name "Head Pharmacist"

Roles: ``patient`` | ``pharmacist`` | ``admin`` (default: ``pharmacist``).
If the email already exists, its password/role/name are updated in place.
"""
import argparse
import sys
from pathlib import Path

# Allow running as a script from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from db import Base, SessionLocal, engine  # noqa: E402
from models import User  # noqa: E402
from security import hash_password  # noqa: E402

ROLES = ("patient", "pharmacist", "admin")


def run(email: str, password: str, role: str, name: str) -> None:
    if role not in ROLES:
        raise SystemExit(f"--role must be one of {ROLES}")
    if len(password) < 8:
        raise SystemExit("--password must be at least 8 characters")

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        action = "Updated" if user else "Created"
        if not user:
            user = User(email=email)
            db.add(user)
        user.hashed_password = hash_password(password)
        user.role = role
        if name:
            user.full_name = name
        db.commit()
        db.refresh(user)
        print(f"{action} {role} account: {user.email} (id={user.id})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--role", default="pharmacist", choices=ROLES)
    ap.add_argument("--name", default="")
    args = ap.parse_args()
    run(args.email, args.password, args.role, args.name)
