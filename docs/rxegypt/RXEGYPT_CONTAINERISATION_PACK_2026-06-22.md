# RxEgypt Containerisation Pack — UI/UX Build Sprint

**Date:** 22 June 2026  
**Project:** RxEgypt / Experts Pharmacy Hurghada  
**Priority:** P0 — queue-imminent build candidate  
**Owner:** Astra Intelligence Services (Misr) / AISE  
**Purpose:** Consolidate the RxEgypt pilot data, repo pointers, seed catalogue and build instructions so tomorrow's full UI/UX web build can start from one containerised source.

---

## 1. Current source of truth

The RxEgypt pilot was found in GitHub history under:

- Repository: `Fly-ai-guy7/expert-spork`
- Commit: `e6458d3851fa513f2e21bafc63dc85638585bad6`
- Commit title: `Scaffold RxEgypt pilot for Experts Pharmacy Hurghada`
- Historical subdirectory: `rxegypt-pilot/`

That commit introduced:

- FastAPI backend
- SQLAlchemy models
- drug search and barcode lookup
- inventory routes
- orders with Rx gating
- auth and PDPL consent
- vanilla HTML/JS frontend
- patient app
- pharmacy POS
- bilingual Dawai patient app
- shared API client
- legal and grant docs
- original 30-drug Egyptian seed database

---

## 2. Medication container status

| Layer | Count | Status |
|---|---:|---|
| Original GitHub seed database | 30 | Found and confirmed |
| Expanded UI/UX seed candidate | 108 | Created in this branch |
| Rx / pharmacist-gated records | 66 | Must remain gated |
| OTC / public sale candidate records | 42 | Still requires pharmacy verification |
| Target expanded catalogue | 250 | Next milestone |

**New data file created for tomorrow:**  
`docs/rxegypt/rxegypt_drug_seed_expanded_108_v0_1.json`

This is a **UI/build seed**, not a production pharmacy catalogue. Records 1–30 are copied from the original seed. Records 31–108 are expansion candidates requiring EDA/pharmacy verification before live use.

---

## 3. Medication category coverage

| Category | Records |
|---|---:|
| Antidiabetic | 10 |
| Gastrointestinal | 10 |
| Antibiotic | 12 |
| Supplement | 10 |
| Cardiovascular | 9 |
| Dermatology | 7 |
| Respiratory | 6 |
| Antihistamine | 6 |
| NSAID | 6 |
| CNS | 4 |
| Analgesic | 5 |
| Lipid-lowering | 4 |
| Antifungal | 4 |
| Ophthalmic | 3 |
| Anticoagulant | 2 |
| Antiplatelet | 2 |
| Antispasmodic | 2 |
| Corticosteroid | 2 |
| ENT | 2 |
| Haematinic | 2 |
| Antiseptic | 1 |
| Antiviral | 2 |
| Controlled Analgesic | 1 |
| Electrolyte | 1 |
| Endocrine | 2 |
| Probiotic | 1 |
| Topical NSAID | 1 |

---

## 4. Data model carried forward

The historical SQLAlchemy `Drug` model supports:

| Field | Purpose |
|---|---|
| `name_en` | English product name |
| `name_ar` | Arabic product name |
| `generic` | Active ingredient / generic descriptor |
| `form` | tablet, capsule, syrup, injection, inhaler, cream, etc. |
| `strength` | labelled strength |
| `category` | therapeutic/product category |
| `manufacturer` | manufacturer / brand owner |
| `barcode` | EAN-13 barcode where verified |
| `price_egp` | Egyptian pound reference price |
| `rx` | prescription / pharmacist-gated flag |

**Important:** records 31–108 use `UNVERIFIED-RXEG-####` placeholder barcode values. They are unique seed identifiers only and must not be treated as real scan codes.

---

## 5. UI/UX build requirements for tomorrow

### Patient-facing layer

Required views:

1. Landing / pharmacy trust page
2. Drug search page
3. Category browsing
4. Product detail card
5. Basket / enquiry flow
6. Rx-gated medicine workflow
7. PDPL consent modal
8. Bilingual EN/AR mode with RTL support
9. WhatsApp pharmacist confirmation handoff
10. Health Information Guide disclaimer layer

### Pharmacist / POS layer

Required views:

1. Pharmacist login
2. Barcode / product search
3. Inventory table
4. Low-stock report
5. Order queue
6. Pending Rx verification queue
7. Pharmacist approval / rejection action
8. Stock adjustment flow
9. Consent log access
10. Admin audit panel

### Non-negotiable compliance behaviours

- No prescription-only medicine is directly orderable without pharmacist verification.
- Rx items must route to `pending_rx_verification`.
- Controlled/high-risk medicines require stricter handling and should be blocked from consumer self-checkout.
- Health Information Guide must remain general-information only.
- No diagnosis.
- No severity scoring.
- No dosage recommendations.
- No substitution recommendations without pharmacist confirmation.
- PDPL consent must be explicit before storing personal or health-related data.

---

## 6. Recommended tomorrow build sequence

### Phase A — Recover and stabilise

1. Restore `rxegypt-pilot/` from commit `e6458d3851fa513f2e21bafc63dc85638585bad6`.
2. Move it into a dedicated repo or top-level app folder.
3. Replace stale Luxor-facing repo confusion with explicit RxEgypt project naming.
4. Add this container pack and expanded seed file as the build baseline.

### Phase B — Data container

1. Load `rxegypt_drug_seed_expanded_108_v0_1.json`.
2. Run schema compatibility check against `Drug`.
3. Add a `verification_status` field in the next model revision if the schema is upgraded.
4. Split records into:
   - `verified_seed`
   - `candidate_seed`
   - `needs_barcode`
   - `needs_price`
   - `needs_rx_review`

### Phase C — UI/UX

1. Build modern bilingual pharmacy UI.
2. Keep patient flow simple: search → product → basket/enquiry → consent/Rx check → WhatsApp/pharmacist handoff.
3. Build pharmacist console as a working operational dashboard, not just mock UI.
4. Add clear visual trust layer: AISE, Experts Pharmacy, PDPL, pharmacist-reviewed.

### Phase D — Hardening

1. Alembic migrations.
2. Pytest coverage for Rx gating and consent.
3. Demo mode + live backend toggle.
4. Paymob placeholder hooks only until credentials are available.
5. EDA/GS1 barcode verification backlog.

---

## 7. Immediate open risks

| Risk | Severity | Mitigation |
|---|---|---|
| Current repo main branch is Luxor-focused, while RxEgypt lives in an old commit | High | Recover to dedicated branch/repo before build |
| Expanded medicine list is not pharmacy/EDA verified | High | Keep `UNVERIFIED-RXEG` IDs and block production use |
| Prices are stale or missing | Medium | Set candidate records to `0.0` until verified |
| Rx flags need pharmacist/legal confirmation | High | Default conservative gating |
| Controlled medicines require strict handling | Critical | Block from public self-checkout |
| No Alembic migrations yet | Medium | Add before production deployment |
| Paymob credentials absent | Medium | Use placeholder hooks only |

---

## 8. Proposed next catalogue milestone

Move from **108 → 250** records by adding:

- paediatric formulations
- common cold/flu products
- dermocosmetics and wound care
- chronic disease SKUs
- diabetes devices and strips
- first-aid products
- mother/baby essentials
- verified Arabic names
- verified EAN-13 codes
- pharmacy-confirmed stock levels
- current EGP prices

---

## 9. Build readiness

[██████░░░░] 60%

**AI time:** approx. 1 focused sprint to recover/containerise baseline.  
**Human comparison time:** 1–2 days for manual repo archaeology + spreadsheet prep.

---

🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜  
RxEgypt · Containerisation Pack · 22 June 2026
