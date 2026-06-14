"""Luxor Guest House — FastAPI backend.

Serves property data from JSON "ledger" files, records booking enquiries to a
JSON file, exposes simple dashboard KPIs, and runs a deterministic concierge
that answers from the local ledger (rooms, tours, policies, FAQ, contacts).

No external services or LLMs are called.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
APP_DIR = Path(__file__).resolve().parent           # .../backend/app
LEDGER_DIR = APP_DIR / "ledger"
REPO_ROOT = APP_DIR.parents[1]                       # .../luxor-guest-house-prototype
DEFAULT_BOOKINGS = REPO_ROOT / "database" / "bookings.json"
BOOKINGS_FILE = Path(os.getenv("BOOKINGS_FILE", str(DEFAULT_BOOKINGS)))

_bookings_lock = Lock()


# --------------------------------------------------------------------------- #
# Ledger helpers
# --------------------------------------------------------------------------- #
def load_ledger(name: str) -> Any:
    """Load a JSON ledger file by name (without extension)."""
    path = LEDGER_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_bookings() -> list[dict]:
    if not BOOKINGS_FILE.exists():
        return []
    try:
        with BOOKINGS_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def write_bookings(bookings: list[dict]) -> None:
    BOOKINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = BOOKINGS_FILE.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(bookings, fh, indent=2, ensure_ascii=False)
    tmp.replace(BOOKINGS_FILE)


# --------------------------------------------------------------------------- #
# App + CORS
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="Luxor Guest House API",
    description="Backend for the Luxor Guest House booking prototype.",
    version="1.0.0",
)

_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_env_origins = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()
]
ALLOWED_ORIGINS = _default_origins + _env_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Allow Vercel preview/production domains in addition to the explicit list.
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #
class BookingIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=40)
    room_id: Optional[str] = Field(None, max_length=80)
    check_in: Optional[str] = Field(None, max_length=40)
    check_out: Optional[str] = Field(None, max_length=40)
    guests: Optional[int] = Field(None, ge=1, le=20)
    tours: list[str] = Field(default_factory=list)
    message: Optional[str] = Field(None, max_length=2000)


class ConciergeIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


# --------------------------------------------------------------------------- #
# Basic + data endpoints
# --------------------------------------------------------------------------- #
@app.get("/")
def root() -> dict:
    contacts = load_ledger("contacts")
    return {
        "service": "Luxor Guest House API",
        "status": "ok",
        "version": "1.0.0",
        "property": contacts.get("property_name", "Luxor Guest House"),
        "endpoints": [
            "/api/rooms",
            "/api/tours",
            "/api/policies",
            "/api/faq",
            "/api/contacts",
            "/api/bookings",
            "/api/dashboard",
            "/api/concierge",
        ],
    }


@app.get("/api/rooms")
def get_rooms() -> list[dict]:
    return load_ledger("rooms")


@app.get("/api/tours")
def get_tours() -> list[dict]:
    return load_ledger("tours")


@app.get("/api/policies")
def get_policies() -> dict:
    return load_ledger("policies")


@app.get("/api/faq")
def get_faq() -> list[dict]:
    return load_ledger("faq")


@app.get("/api/contacts")
def get_contacts() -> dict:
    return load_ledger("contacts")


# --------------------------------------------------------------------------- #
# Bookings
# --------------------------------------------------------------------------- #
@app.get("/api/bookings")
def get_bookings() -> list[dict]:
    return read_bookings()


@app.post("/api/bookings", status_code=201)
def create_booking(payload: BookingIn) -> dict:
    record = payload.model_dump()
    record["id"] = uuid.uuid4().hex[:12]
    record["created_at"] = datetime.now(timezone.utc).isoformat()
    record["status"] = "new"

    with _bookings_lock:
        bookings = read_bookings()
        bookings.append(record)
        write_bookings(bookings)

    return {"ok": True, "booking": record}


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
@app.get("/api/dashboard")
def get_dashboard() -> dict:
    rooms = load_ledger("rooms")
    tours = load_ledger("tours")
    contacts = load_ledger("contacts")
    bookings = read_bookings()

    priced_rooms = [r["reference_price"] for r in rooms if r.get("reference_price")]
    avg_room_price = round(sum(priced_rooms) / len(priced_rooms), 2) if priced_rooms else 0
    bookable_tours = [t for t in tours if not t.get("price_on_request")]
    on_request_tours = [t for t in tours if t.get("price_on_request")]

    recent = sorted(bookings, key=lambda b: b.get("created_at", ""), reverse=True)[:5]

    return {
        "kpis": {
            "total_rooms": len(rooms),
            "total_tours": len(tours),
            "bookable_tours": len(bookable_tours),
            "tours_on_request": len(on_request_tours),
            "total_enquiries": len(bookings),
            "new_enquiries": sum(1 for b in bookings if b.get("status") == "new"),
            "avg_room_reference_price_gbp": avg_room_price,
            "rating": contacts.get("ratings", {}).get("score"),
            "reviews": contacts.get("ratings", {}).get("reviews"),
        },
        "recent_enquiries": recent,
        "rooms": rooms,
        "tours": tours,
    }


# --------------------------------------------------------------------------- #
# Concierge (deterministic, ledger-backed)
# --------------------------------------------------------------------------- #
def _format_room(room: dict) -> str:
    price = room.get("reference_price")
    price_txt = (
        f"from £{price} {room.get('price_note', '')}".strip()
        if price is not None
        else "price on request"
    )
    return (
        f"{room['name']} — {room.get('size_m2')} m², sleeps "
        f"{room.get('capacity_adults')} ({room.get('beds')}). {price_txt}."
    )


def _format_tour(tour: dict) -> str:
    if tour.get("price_on_request"):
        price_txt = "price on request"
    else:
        price_txt = f"${tour.get('price')}"
    note = f" ({tour['notes']})" if tour.get("notes") else ""
    return f"{tour['name']} — {price_txt}{note}."


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def concierge_reply(message: str) -> dict:
    msg = message.lower()
    tokens = _tokens(message)
    rooms = load_ledger("rooms")
    tours = load_ledger("tours")
    policies = load_ledger("policies")
    faq = load_ledger("faq")
    contacts = load_ledger("contacts")

    sources: list[str] = []
    parts: list[str] = []

    # --- FAQ matches (tag overlap) ---
    faq_hits = []
    for item in faq:
        tag_tokens = set()
        for tag in item.get("tags", []):
            tag_tokens |= _tokens(tag)
        if tag_tokens & tokens:
            faq_hits.append(item)
    if faq_hits:
        sources.append("faq")
        for item in faq_hits[:3]:
            parts.append(item["answer"])

    # --- Room matches ---
    room_keywords = {"room", "rooms", "apartment", "studio", "stay", "bed",
                     "sleep", "price", "prices", "rate", "rates", "night",
                     "accommodation", "river", "view"}
    if tokens & room_keywords:
        matched = [
            r for r in rooms
            if _tokens(r["name"]) & tokens or _tokens(" ".join(r.get("amenities", []))) & tokens
        ]
        chosen = matched if matched else rooms
        sources.append("rooms")
        parts.append("Rooms you might like:\n- " + "\n- ".join(_format_room(r) for r in chosen[:5]))

    # --- Tour matches ---
    tour_keywords = {"tour", "tours", "trip", "trips", "excursion", "excursions",
                     "visit", "balloon", "felucca", "temple", "valley", "aswan",
                     "cairo", "karnak", "luxor", "safari", "nile", "abu", "simbel"}
    if tokens & tour_keywords:
        matched = [t for t in tours if _tokens(t["name"]) & tokens or _tokens(t.get("area", "")) & tokens]
        chosen = matched if matched else tours
        sources.append("tours")
        parts.append("Tours we can arrange:\n- " + "\n- ".join(_format_tour(t) for t in chosen[:6]))

    # --- Policy matches ---
    policy_keywords = {"breakfast", "prepayment", "deposit", "card", "payment",
                       "pay", "cancel", "cancellation", "refund", "checkin",
                       "check", "checkout", "policy", "policies", "tax", "taxes"}
    if tokens & policy_keywords:
        sources.append("policies")
        parts.append(policies["booking"]["summary"])
        ci = policies["check_in_out"]
        parts.append(f"Check-in from {ci['check_in_from']}, check-out until {ci['check_out_until']}.")

    # --- Contact / WhatsApp ---
    contact_keywords = {"contact", "whatsapp", "phone", "call", "email",
                        "reach", "message", "ahmed", "book", "booking",
                        "reserve", "enquire", "enquiry", "address", "location", "where"}
    if (tokens & contact_keywords) or not parts:
        sources.append("contacts")
        parts.append(
            f"To book or ask anything, message {contacts['primary_contact']} on WhatsApp "
            f"at {contacts['whatsapp_display']} ({contacts['whatsapp_link']}) "
            f"or email {contacts['email']}. We are at {contacts['address']}."
        )

    if not parts:
        parts.append(
            "Welcome to Luxor Guest House! I can help with rooms, tours, breakfast, "
            "payment and check-in. What would you like to know?"
        )

    # de-duplicate sources, preserve order
    seen: set[str] = set()
    ordered_sources = [s for s in sources if not (s in seen or seen.add(s))]

    return {
        "reply": "\n\n".join(parts),
        "sources": ordered_sources,
        "whatsapp_link": contacts["whatsapp_link"],
    }


@app.post("/api/concierge")
def post_concierge(payload: ConciergeIn) -> dict:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")
    return concierge_reply(payload.message)
