"""Build the RxEgypt drug seed from a verified, citable open dataset.

Source
------
karem505/egyptian-drug-database (GitHub) — 24,868 medicines on the Egyptian
market: bilingual trade names, scientific composition, manufacturer, drug class,
route, and EGP retail price. Released under CC0-1.0 (public domain).

    https://github.com/karem505/egyptian-drug-database

This script downloads the dataset, verifies its SHA-256, maps it onto the
RxEgypt `Drug` schema, derives a CONSERVATIVE Rx flag, and writes:

    seed/drugs_egypt.json   (the seed consumed by seed_drugs.py)
    seed/PROVENANCE.md      (source, license, hash, field mapping, Rx rules)

Run from the backend/ directory:

    python seed/build_egyptian_drugs.py            # download + build
    python seed/build_egyptian_drugs.py --offline  # reuse a local cached copy

IMPORTANT — Rx derivation is HEURISTIC. The source dataset has no
prescription/OTC field. We default every medicine to prescription-only (the
legally safe choice) and down-classify to OTC only for an explicit allow-list of
non-prescription drug classes. Every `rx` value MUST be reconciled against the
Egyptian Drug Authority (EDA) register before go-live. See PROVENANCE.md.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path

RAW_URL = (
    "https://raw.githubusercontent.com/karem505/"
    "egyptian-drug-database/main/data/egyptian-drugs.json"
)
SOURCE_REPO = "https://github.com/karem505/egyptian-drug-database"
SOURCE_LICENSE = "CC0-1.0"
# Pin: integrity is anchored to this content hash. A mismatch means upstream
# changed and the build must be re-reviewed before the new data is trusted.
EXPECTED_SHA256 = "7dd19a86100c3be569afc71ebfa6e803c4ccc79ef8f4ca289d09cf77dcc5662a"

SEED_DIR = Path(__file__).resolve().parent
# Gzip-compressed to keep the repo lean (~1.3 MB vs ~8 MB raw). seed_drugs.py
# reads it transparently.
OUT_JSON = SEED_DIR / "drugs_egypt.json.gz"
CACHE = SEED_DIR / ".egyptian-drugs.source.json"
PROVENANCE = SEED_DIR / "PROVENANCE.md"

# --- Rx derivation rules (substring match on UPPER-CASED drug_class) ---------
# Deny-list wins over allow-list. Anything unmatched defaults to Rx (safe).
RX_DENY = (
    "ANTIBIOTIC", "ANTIBACTERIAL", "ANTIVIRAL", "ANTIRETROVIRAL", "ANTIFUNGAL",
    "ANTINEOPLASTIC", "CHEMOTHERAP", "ONCOLOGY", "PSYCHIATRIC", "ANTIDEPRESS",
    "ANTIPSYCHOTIC", "ANXIOLYTIC", "HYPNOTIC", "SEDATIVE", "OPIOID", "NARCOTIC",
    "CONTROLLED", "HORMONE", "CORTICOSTEROID", "STEROID", "INSULIN",
    "ANTIDIABETIC", "HYPOGLYCEMIC", "CARDIO", "ANTIHYPERTENS", "ANTIARRHYTH",
    "ANTICOAGULANT", "ANTIPLATELET", "STATIN", "ANTIHYPERLIPID", "ANTIEPILEPTIC",
    "ANTICONVULS", "IMMUNOSUPPRESS", "IMMUNO", "VACCINE", "THYROID",
    "TUBERCULOSIS", "ANTI-PARKINSON", "PARKINSON", "GLAUCOMA", "DIURETIC",
    "BRONCHODILATOR", "MUSCLE RELAXANT", "PROTON PUMP", "ANTI-COAGULANT",
    "ANTIEMETIC", "ANTI-MIGRAINE", "ERECTILE", "CONTRACEPT", "FERTILITY",
)
RX_ALLOW = (
    "SKIN CARE", "HAIR CARE", "SUN BLOCK", "SUNBLOCK", "SOAP", "MASSAGE",
    "COSMETIC", "MOISTURIZ", "SHAMPOO", "BABY CARE", "ORAL CARE", "DENTAL",
    "MOUTH", "DEODORANT", "VITAMIN", "MULTIVITAMIN", "MINERAL", "SUPPLEMENT",
    "CALCIUM", "OMEGA", "PROBIOTIC", "NUTRITION", "FORMULA", "ANTACID",
    "FLATULENT", "LAXATIVE", "REHYDRATION", "COLD PRODUCTS", "COUGH",
    "DECONGESTANT", "THROAT", "LOZENGE", "ANTISEPTIC", "DISINFECTANT", "WOUND",
    "FIRST AID", "ANTI-HISTAMINE", "ANTIHISTAMINE", "ANTI-ALLERGY", "ANTIPYRETIC",
    "EMOLLIENT", "MEDICAL DEVICE",
)


def derive_rx(drug_class: str) -> bool:
    cls = (drug_class or "").upper()
    if any(k in cls for k in RX_DENY):
        return True
    if any(k in cls for k in RX_ALLOW):
        return False
    return True  # unknown / unmatched -> prescription-only (safe default)


def normalize_route(route: str) -> str:
    r = (route or "").strip().upper()
    return {
        "ORAL.SOLID": "oral solid", "ORAL.LIQUID": "oral liquid",
        "INJECTION": "injection", "TOPICAL": "topical", "EFF": "effervescent",
        "SPRAY": "spray", "EYE": "eye", "VAGINAL": "vaginal", "MOUTH": "oral",
        "RECTAL": "rectal", "SOAP": "soap", "UNKNOWN": "", "": "",
    }.get(r, r.lower())


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "rxegypt-seed-build"})
    with urllib.request.urlopen(req, timeout=180) as resp:  # noqa: S310 (trusted host)
        return resp.read()


def transform(records: list[dict]) -> list[dict]:
    out = []
    rx_tag = f"egyptian-drug-database@sha256:{EXPECTED_SHA256[:12]} (heuristic)"
    for r in records:
        name_en = (r.get("commercial_name_en") or "").strip()
        if not name_en:
            continue
        cls = (r.get("drug_class") or "").strip()
        try:
            price = float(r.get("price_egp") or 0.0)
        except (TypeError, ValueError):
            price = 0.0
        out.append({
            "name_en": name_en,
            "name_ar": (r.get("commercial_name_ar") or "").strip(),
            "generic": (r.get("scientific_name") or "").strip(),
            "form": normalize_route(r.get("route", "")),
            "strength": "",  # not provided by source
            "category": cls,
            "manufacturer": (r.get("manufacturer") or "").strip(),
            "barcode": "",   # not provided by source; populate from EDA/GS1 later
            "price_egp": round(price, 2),
            "rx": derive_rx(cls),
            "rx_source": rx_tag,
        })
    return out


def write_provenance(n_total: int, n_rx: int, n_otc: int, sha: str) -> None:
    PROVENANCE.write_text(f"""# Drug seed data — provenance

**Generated:** {date.today().isoformat()} · by `seed/build_egyptian_drugs.py`

## Source
- **Dataset:** Egyptian drug database — {SOURCE_REPO}
- **File:** `data/egyptian-drugs.json`
- **License:** {SOURCE_LICENSE} (public-domain dedication)
- **Integrity (SHA-256):** `{sha}`
- **Records imported:** {n_total:,} ({n_rx:,} Rx / {n_otc:,} OTC)

> The source is a community-maintained, CC0 dataset of medicines on the Egyptian
> market. It is **not** an official Egyptian Drug Authority (EDA) feed. Trade
> names should be cross-referenced against the EDA register.

## Field mapping (source → RxEgypt `Drug`)
| RxEgypt field | Source field | Notes |
|---|---|---|
| `name_en` | `commercial_name_en` | trade name |
| `name_ar` | `commercial_name_ar` | Arabic name (often short) |
| `generic` | `scientific_name` | active ingredient(s) |
| `manufacturer` | `manufacturer` | |
| `category` | `drug_class` | hierarchical, e.g. `ANTIBIOTIC.QUINOLONE` |
| `form` | `route` | normalized (e.g. `ORAL.SOLID` → `oral solid`) |
| `price_egp` | `price_egp` | EGP retail; `0.0` where missing |
| `strength` | — | not in source; left blank |
| `barcode` | — | not in source; left blank (add from EDA/GS1) |
| `rx` | *(derived)* | see below |

## ⚠️ Rx derivation is HEURISTIC — confirm against EDA before go-live
The source has **no** prescription/OTC indicator. We derive `rx` from
`drug_class`:
1. If the class matches a prescription **deny-list** keyword → `rx = true`.
2. Else if it matches a non-prescription **allow-list** keyword → `rx = false`.
3. Otherwise → `rx = true` (unknown classes default to prescription-only).

This deliberately **over-gates**: erring toward "prescription required" means an
extra pharmacist check, never an unauthorized dispense. Every `rx` value carries
`rx_source = "{f'egyptian-drug-database@sha256:{sha[:12]} (heuristic)'}"`.
The legal Rx schedule of record is the EDA register, not this dataset.

_Regenerate with:_ `python seed/build_egyptian_drugs.py`
""", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="use the cached source copy instead of downloading")
    args = ap.parse_args()

    if args.offline and CACHE.exists():
        blob = CACHE.read_bytes()
    else:
        print(f"Downloading {RAW_URL} …")
        blob = download(RAW_URL)
        CACHE.write_bytes(blob)

    sha = hashlib.sha256(blob).hexdigest()
    if sha != EXPECTED_SHA256:
        raise SystemExit(
            f"SHA-256 mismatch!\n  expected {EXPECTED_SHA256}\n  got      {sha}\n"
            "Upstream data changed — review before trusting. Update EXPECTED_SHA256 "
            "only after re-reviewing the Rx derivation against the new data."
        )

    records = json.loads(blob)
    drugs = transform(records)
    n_rx = sum(d["rx"] for d in drugs)
    n_otc = len(drugs) - n_rx

    payload = json.dumps(drugs, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.open(OUT_JSON, "wb") as fh:
        fh.write(payload)
    write_provenance(len(drugs), n_rx, n_otc, sha)
    print(f"Wrote {OUT_JSON.name}: {len(drugs):,} drugs ({n_rx:,} Rx / {n_otc:,} OTC)")
    print(f"Wrote {PROVENANCE.name}")


if __name__ == "__main__":
    main()
