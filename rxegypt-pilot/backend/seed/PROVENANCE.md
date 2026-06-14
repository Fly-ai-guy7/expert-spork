# Drug seed data — provenance

**Generated:** 2026-06-01 · by `seed/build_egyptian_drugs.py`

## Source
- **Dataset:** Egyptian drug database — https://github.com/karem505/egyptian-drug-database
- **File:** `data/egyptian-drugs.json`
- **License:** CC0-1.0 (public-domain dedication)
- **Integrity (SHA-256):** `7dd19a86100c3be569afc71ebfa6e803c4ccc79ef8f4ca289d09cf77dcc5662a`
- **Records imported:** 24,868 (14,907 Rx / 9,961 OTC; 311 controlled)

> `controlled` flags narcotics/psychotropics matched by class or active
> ingredient (heuristic — reconcile against the EDA schedule). LEGAL: controlled
> substances are **never** orderable online; `POST /orders` rejects them.

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
`drug_class` (which is hierarchical, e.g. `ANTIBIOTIC.QUINOLONE`):
1. If the class matches the **hard prescription list** → `rx = true`
   (this always wins — covers antibiotics, antivirals, cardiovascular,
   antidiabetics, steroids/hormones, psychiatric, oncology, etc.).
2. Else if it matches the **OTC allow-list** → `rx = false`
   (personal care, vitamins/supplements, and well-established symptomatic OTC
   classes: cold/cough, antacids, antiseptics, antipyretics, antihistamines…).
3. Otherwise → `rx = true` (unknown classes default to prescription-only).

This deliberately **over-gates**: ambiguous classes (e.g. WEIGHT LOSS, SEXUAL
TONIC, SLEEP AID, leucovorin) stay Rx. The rules were validated against the full
dataset with **zero** antibiotic / cardiovascular / antidiabetic / steroid
medicines leaking into OTC. Erring toward "prescription required" means an extra
pharmacist check, never an unauthorized dispense. Every `rx` value carries
`rx_source = "egyptian-drug-database@sha256:7dd19a86100c (heuristic)"`.
The legal Rx schedule of record is the EDA register, not this dataset.

_Regenerate with:_ `python seed/build_egyptian_drugs.py`
