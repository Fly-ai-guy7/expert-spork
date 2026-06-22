# RxEgypt P0 / Q-Imminent Build Plan

## Objective

Recover the RxEgypt Experts Pharmacy Hurghada pilot from the historical scaffold and move it into an immediate build-ready state for a fast Wi-Fi co-working sprint.

## Current confirmed state

- Historical scaffold exists under `rxegypt-pilot/`.
- Backend: FastAPI, SQLAlchemy, JWT auth, drugs, inventory, orders.
- Frontend: patient app, pharmacy POS, Dawai bilingual patient app, API client.
- Seed DB currently confirmed at 30 medication records.
- Target seed expansion: 250 medication records.
- Rx gating, PDPL consent, bilingual health-information disclaimers already scaffolded.

## Immediate branch

`rxegypt-p0-drug-expansion-250`

## Tomorrow build order

### 1. Restore / isolate RxEgypt app

- Confirm branch checkout from the historical RxEgypt scaffold.
- Verify `rxegypt-pilot/backend` starts locally.
- Verify `rxegypt-pilot/frontend` opens locally.
- Confirm Swagger docs at `/docs`.

### 2. Data expansion

- Expand `backend/seed/drugs_egypt.json` from 30 to 250 records.
- Keep the existing schema unchanged for fast compatibility:
  - `name_en`
  - `name_ar`
  - `generic`
  - `form`
  - `strength`
  - `category`
  - `manufacturer`
  - `barcode`
  - `price_egp`
  - `rx`
- Add pharmacist verification notes outside the live model until schema migration is introduced.

### 3. Safety / compliance behaviour

- Default uncertain prescription-sensitive products to `rx: true`.
- Do not allow self-serve checkout for controlled medicines.
- Require pharmacist verification before Rx order fulfilment.
- Keep Health Information Guide non-diagnostic.
- Keep PDPL consent before health-data processing.

### 4. UI integration

- Confirm search by brand, Arabic name, generic and category.
- Confirm barcode lookup from POS screen.
- Confirm Rx warning state in patient flow.
- Confirm low-stock report still works after seed expansion.

### 5. Production blockers

- Replace generated/test barcodes with verified pharmacy/EAN/GS1 data.
- Validate Egyptian Rx/control status with pharmacist/legal review.
- Validate prices against Experts Pharmacy inventory.
- Add Alembic migrations before production.
- Add tests for Rx gating and consent flows.

## Acceptance checklist

- [ ] Seed count returns exactly 250 records.
- [ ] Seeder is idempotent.
- [ ] Backend starts cleanly.
- [ ] Frontend demo and live API modes still work.
- [ ] Rx products route to `pending_rx_verification`.
- [ ] OTC products can proceed without Rx verification.
- [ ] No health screen presents diagnosis, severity or Rx suggestions.
- [ ] Readme and legal notes show P0 status and production guardrails.

## Build readiness

[██████░░░░] 60%

AI time so far: under 1 hour
Human comparison time: 1-2 days to locate, recover, classify and prepare branch context

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
RxEgypt · P0 Q-Imminent Build Plan · 22 June 2026
