"""Pytest fixtures — isolated SQLite app + seeded drugs per test."""
import os

# Configure the app for testing BEFORE importing any app module (settings are
# cached and the engine is built at import time).
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401  (registers tables on Base.metadata)
from db import Base, get_db
from main import app
from models import Drug, Inventory, User
from security import hash_password


@pytest.fixture()
def session():
    # A single shared in-memory connection for the test's lifetime.
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = TestingSession()

    # Seed a couple of drugs: one OTC, one Rx.
    otc = Drug(name_en="Panadol", name_ar="بنادول", generic="Paracetamol",
               barcode="6223000000010", price_egp=20.0, rx=False)
    rx = Drug(name_en="Augmentin", name_ar="أوجمنتين", generic="Amoxicillin/Clav",
              barcode="6223000000027", price_egp=96.0, rx=True)
    db.add_all([otc, rx])
    db.flush()
    db.add_all([Inventory(drug_id=otc.id, quantity=50),
                Inventory(drug_id=rx.id, quantity=50)])
    db.commit()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture()
def client(session):
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def patient_token(client):
    client.post("/api/v1/auth/register",
                json={"email": "pat@x.com", "password": "password1"})
    r = client.post("/api/v1/auth/login",
                    data={"username": "pat@x.com", "password": "password1"})
    token = r.json()["access_token"]
    # Grant PDPL consent so order-flow tests reflect a real, consented patient.
    client.post("/api/v1/auth/consent", json={"granted": True},
                headers={"Authorization": f"Bearer {token}"})
    return token


@pytest.fixture()
def pharmacist_token(client, session):
    session.add(User(email="ph@x.com", hashed_password=hash_password("password1"),
                     role="pharmacist"))
    session.commit()
    r = client.post("/api/v1/auth/login",
                    data={"username": "ph@x.com", "password": "password1"})
    return r.json()["access_token"]
