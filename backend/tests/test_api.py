"""API tests for the Luxor Guest House backend.

Booking tests are isolated by pointing ``BOOKINGS_FILE`` at a temporary file
*before* the app is imported, so they never touch the demo/production booking
store in ``database/bookings.json``.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make the backend package importable when pytest is run from backend/.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """A TestClient backed by an isolated, temporary bookings file.

    The app reads ``BOOKINGS_FILE`` at import time, so we set the env var and
    (re)import the module within the fixture to pick up the temp path.
    """
    bookings_file = tmp_path / "bookings.json"
    monkeypatch.setenv("BOOKINGS_FILE", str(bookings_file))

    import app.main as main

    main = importlib.reload(main)
    assert main.BOOKINGS_FILE == bookings_file

    with TestClient(main.app) as test_client:
        yield test_client


def test_root_returns_service_status_and_endpoints(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "Luxor Guest House API"
    assert isinstance(body["endpoints"], list) and body["endpoints"]


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_rooms_non_empty(client):
    resp = client.get("/api/rooms")
    assert resp.status_code == 200
    rooms = resp.json()
    assert isinstance(rooms, list) and len(rooms) > 0
    assert "name" in rooms[0]


def test_tours_non_empty(client):
    resp = client.get("/api/tours")
    assert resp.status_code == 200
    tours = resp.json()
    assert isinstance(tours, list) and len(tours) > 0
    assert "name" in tours[0]


def test_policies_valid(client):
    resp = client.get("/api/policies")
    assert resp.status_code == 200
    policies = resp.json()
    assert isinstance(policies, dict)
    assert "booking" in policies and "check_in_out" in policies


def test_faq_returns_data(client):
    resp = client.get("/api/faq")
    assert resp.status_code == 200
    faq = resp.json()
    assert isinstance(faq, list) and len(faq) > 0
    assert "answer" in faq[0]


def test_contacts_returns_property_and_rating(client):
    resp = client.get("/api/contacts")
    assert resp.status_code == 200
    contacts = resp.json()
    assert "whatsapp_link" in contacts
    assert "ratings" in contacts


def test_dashboard_returns_kpis(client):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert "kpis" in body
    kpis = body["kpis"]
    assert kpis["total_rooms"] > 0
    assert kpis["total_tours"] > 0


def test_concierge_is_deterministic_and_ledger_backed(client):
    payload = {"message": "Which rooms have a river view?"}
    first = client.post("/api/concierge", json=payload)
    second = client.post("/api/concierge", json=payload)
    assert first.status_code == 200
    assert first.json() == second.json()  # deterministic
    body = first.json()
    assert body["reply"]
    assert "rooms" in body["sources"]
    assert body["whatsapp_link"].startswith("https://wa.me/")


def test_create_booking_uses_isolated_file(client, tmp_path):
    payload = {"name": "Test Guest", "email": "test@example.com", "guests": 2}
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["ok"] is True
    booking = body["booking"]
    assert booking["name"] == "Test Guest"
    assert booking["status"] == "new"
    assert booking["id"]
    # Written to the temporary store, not the demo data.
    assert (tmp_path / "bookings.json").exists()


def test_get_bookings_returns_created_test_booking(client):
    # Empty to start (isolated file).
    assert client.get("/api/bookings").json() == []

    client.post(
        "/api/bookings",
        json={"name": "Second Guest", "email": "second@example.com", "guests": 3},
    )
    bookings = client.get("/api/bookings").json()
    assert len(bookings) == 1
    assert bookings[0]["name"] == "Second Guest"
