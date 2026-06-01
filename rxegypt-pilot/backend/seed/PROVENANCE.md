# Drug seed data — provenance

**Generated:** 2026-06-01 · by `seed/build_egyptian_drugs.py`

## Source
- **Dataset:** Egyptian drug database — https://github.com/karem505/egyptian-drug-database
- **File:** `data/egyptian-drugs.json`
- **License:** CC0-1.0 (public-domain dedication)
- **Integrity (SHA-256):** `7dd19a86100c3be569afc71ebfa6e803c4ccc79ef8f4ca289d09cf77dcc5662a`
- **Records imported:** 24,868 (16,066 Rx / 8,802 OTC)

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
`rx_source = "egyptian-drug-database@sha256:7dd19a86100c (heuristic)"`.
The legal Rx schedule of record is the EDA register, not this dataset.

_Regenerate with:_ `python seed/build_egyptian_drugs.py`
