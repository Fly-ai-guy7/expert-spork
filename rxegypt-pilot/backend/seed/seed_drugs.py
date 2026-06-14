"""Seed the drug catalogue from the verified Egyptian dataset.

Reads ``drugs_egypt.json.gz`` (produced by ``build_egyptian_drugs.py`` from the
CC0 Egyptian drug database — see PROVENANCE.md) and bulk-loads it into the
``drugs`` table.

By default this is a no-op if the table is already populated. Use ``--force`` to
wipe and reload the catalogue.

Usage (from the ``backend/`` directory)::

    python seed/build_egyptian_drugs.py     # fetch + build the seed file first
    python seed/seed_drugs.py               # load if empty
    python seed/seed_drugs.py --force       # wipe + reload
"""
import argparse
import gzip
import json
import sys
from pathlib import Path

# Allow running as a script from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, func, select  # noqa: E402

from db import Base, SessionLocal, engine  # noqa: E402
from models import Drug, Inventory  # noqa: E402

SEED_GZ = Path(__file__).with_name("drugs_egypt.json.gz")
BATCH = 2000


def _load_records() -> list[dict]:
    if not SEED_GZ.exists():
        raise SystemExit(
            f"{SEED_GZ.name} not found. Run: python seed/build_egyptian_drugs.py"
        )
    with gzip.open(SEED_GZ, "rb") as fh:
        return json.loads(fh.read())


def run(force: bool = False) -> None:
    Base.metadata.create_all(engine)
    records = _load_records()

    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Drug))
        if count and not force:
            print(f"Drugs table already has {count} rows — skipping "
                  f"(use --force to reload).")
            return
        if count and force:
            db.execute(delete(Inventory))
            db.execute(delete(Drug))
            db.commit()
            print(f"Cleared {count} existing drugs.")

        for i in range(0, len(records), BATCH):
            db.bulk_insert_mappings(Drug, records[i:i + BATCH])
            db.commit()

    print(f"Seeded {len(records):,} drugs.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="wipe and reload")
    run(force=ap.parse_args().force)
