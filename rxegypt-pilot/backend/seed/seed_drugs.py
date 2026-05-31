"""Seed the drug database from ``drugs_egypt.json``.

Idempotent: a drug is matched on its EAN-13 barcode; existing rows are updated
in place. Each seeded drug also gets an inventory row (default stock 50).

Usage (from the ``backend/`` directory)::

    python seed/seed_drugs.py
"""
import json
import sys
from pathlib import Path

# Allow running as a script from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import Base, SessionLocal, engine  # noqa: E402
from models import Drug, Inventory  # noqa: E402

SEED_FILE = Path(__file__).with_name("drugs_egypt.json")
DEFAULT_STOCK = 50


def run() -> None:
    Base.metadata.create_all(engine)
    records = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    created = updated = 0
    with SessionLocal() as db:
        for rec in records:
            drug = (
                db.query(Drug).filter(Drug.barcode == rec["barcode"]).one_or_none()
                if rec.get("barcode")
                else None
            )
            if drug is None:
                drug = Drug(**rec)
                db.add(drug)
                db.flush()
                db.add(Inventory(drug_id=drug.id, quantity=DEFAULT_STOCK))
                created += 1
            else:
                for key, value in rec.items():
                    setattr(drug, key, value)
                updated += 1
        db.commit()

    print(f"Seeded drugs — created: {created}, updated: {updated}")


if __name__ == "__main__":
    run()
