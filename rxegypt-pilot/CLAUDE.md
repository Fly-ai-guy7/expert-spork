# CLAUDE.md — RxEgypt Pilot: Experts Pharmacy Hurghada
## Astra Intelligence Services (Misr) — AISE Internal

---

## PROJECT OVERVIEW

RxEgypt is a B2B SaaS pharmacy management and patient-facing platform.
Pilot client: **Experts Pharmacy Hurghada** — Al Ahyaa, Red Sea Governorate, Egypt.
Built by AISE. Stack: FastAPI (backend) + PostgreSQL + HTML/JS frontend.
Grant funding track: ITIDA PDP + ITAC Round 40 + UNDP Digital Health.

---

## REPO LAYOUT

```
rxegypt-pilot/
├── CLAUDE.md                  ← you are here
├── README.md
├── docker-compose.yml         ← local full stack (db + backend + frontend)
├── frontend/
│   ├── index.html             ← patient-facing app (Experts Pharmacy branded)
│   ├── pharmacy-pos.html      ← pharmacist POS (barcode, stock, Rx queue)
│   ├── dawai-patient.html     ← bilingual AR/EN patient drug app + Health Info Guide
│   ├── rxegypt-api.js         ← shared API client (demo + live modes)
│   ├── config.js              ← demo ↔ live switch (backend URL)
│   ├── Dockerfile             ← static server; injects config.js from env
│   └── docker-entrypoint.sh
├── backend/
│   ├── main.py                ← FastAPI entry point
│   ├── Dockerfile             ← production backend image
│   ├── fly.toml               ← Fly.io deploy (release: migrate + seed)
│   ├── config.py              ← settings (env-driven)
│   ├── db.py                  ← engine + session
│   ├── models.py              ← SQLAlchemy models
│   ├── schemas.py             ← Pydantic schemas
│   ├── security.py            ← JWT + password hashing + role guards
│   ├── payments.py            ← Paymob client + MOCK mode + HMAC verify
│   ├── routes/
│   │   ├── drugs.py           ← drug search + barcode lookup
│   │   ├── inventory.py       ← stock management
│   │   ├── orders.py          ← orders + Rx gating/queue + pay + fulfill
│   │   ├── payments.py        ← mock confirm + Paymob callback
│   │   └── auth.py            ← JWT auth + PDPL consent + data-subject rights
│   ├── seed/
│   │   ├── build_egyptian_drugs.py ← fetch+verify CC0 dataset → seed (provenance)
│   │   ├── drugs_egypt.json.gz ← 24,868-drug Egyptian catalogue (built)
│   │   ├── PROVENANCE.md       ← source, license, SHA-256, Rx derivation rules
│   │   ├── seed_drugs.py       ← bulk loader (--force to reload)
│   │   └── create_user.py      ← CLI to create pharmacist/admin accounts
│   ├── migrations/            ← Alembic (env.py + versions/)
│   ├── alembic.ini
│   ├── tests/                 ← pytest suite (isolated SQLite)
│   └── requirements.txt
├── legal/
│   ├── RXEG-LEGAL-001.md      ← Egyptian regulatory compliance framework
│   └── RXEG-GRANT-001.md      ← Grant funding strategy
└── docs/
    └── api-spec.md
```

---

## CURRENT BUILD STATUS

| Component | Status | Notes |
|---|---|---|
| Patient frontend (index.html) | ✅ Live-wired | Browse-free; login + PDPL consent at checkout; backend Rx-WhatsApp |
| Pharmacy POS (pharmacy-pos.html) | ✅ Live-wired | Pharmacist login (role-checked) + real `PUT /inventory` writes |
| Patient drug app (dawai-patient.html) | ✅ Scaffolded | Bilingual AR/EN, RTL (read-only search) |
| Health Information Guide | ✅ Scaffolded | Renamed from symptom checker; disclaimers; no severity/Rx |
| API client (rxegypt-api.js) | ✅ Live-wired | Demo + live; auth helpers, per-role token, 401/403 handling |
| Frontend config (config.js) | ✅ Built | Single switch for demo ↔ live (backend URL) |
| FastAPI backend | ✅ Scaffolded | JWT auth, drugs, inventory, orders |
| SQLAlchemy models | ✅ Scaffolded | Drug, Inventory, User, Order, OrderItem, Consent |
| Drug catalogue | ✅ Real data (24,868) | CC0 Egyptian dataset, SHA-256 verified; Rx flags heuristic — confirm vs EDA |
| Rx drug gating | ✅ Scaffolded | Order → pending_rx_verification + WhatsApp + pharmacist verify |
| Pharmacist Rx queue | ✅ Live-wired | `GET /orders/pending-rx` + approve/reject in POS UI |
| PDPL consent flow | ✅ Scaffolded | Bilingual modal; logged to `consents` with timestamp |
| PDPL data-subject rights | ✅ Built | Consent status/withdraw, data export, account erasure (anonymize) |
| Payment flow (Paymob) | 🟡 Built + mock | Full lifecycle (pay→paid→fulfilled) works in MOCK mode; live 3-step + HMAC callback wired, needs credentials to test |
| Alembic migrations | ✅ Scaffolded | `alembic upgrade head` (initial schema) |
| Backend tests (pytest) | ✅ Scaffolded | 47 tests: Rx gating + queue, payments lifecycle, consent + PDPL rights, auth, inventory, drugs, Rx derivation |
| EDA Track & Trace integration | 🔴 Not started | Phase 2 |
| Deployment (Docker + Fly.io) | ✅ Built | backend Dockerfile + fly.toml; docker-compose for local full stack |
| UHI (Universal Health Insurance) API | 🔴 Not started | Phase 3 |

---

## LEGAL FLAGS — DO NOT SHIP WITHOUT THESE

See `legal/RXEG-LEGAL-001.md` for the authoritative list. Summary:

1. **Rx drug gating** — `rx: true` drugs not orderable without pharmacist
   verification (WhatsApp confirmation flow). ✅ scaffolded — review before go-live.
2. **Health Information Guide disclaimers** — bilingual (EN+AR) on every screen,
   no severity ratings, no Rx suggestions. ✅ scaffolded.
3. **PDPL consent** — explicit consent before any data is stored, logged with
   timestamp. ✅ scaffolded. Data-subject rights (withdraw / export / erasure) ✅ built.
4. **AISE liability shield** — Platform Service Agreement signed before go-live
   (Michael Gamal action). 🔴 outstanding.

---

## PRIORITY NEXT TASKS

1. **Reconcile Rx flags vs EDA register** — the imported `rx` values are
   heuristic (see seed/PROVENANCE.md); confirm scheduling before go-live.
2. **Paymob go-live** — set credentials, validate the HMAC callback against live
   Paymob docs, and register the callback URL.
3. Add **barcodes + strengths** to the catalogue (EDA/GS1) — source lacks both.
4. **Fulfillment UI** — POS view of paid orders to mark fulfilled.
5. **EDA Track & Trace** prep — GS1 barcode serialization groundwork.

---

## AISE CONTEXT

- **Company:** Astra Intelligence Services (Misr) — AISE
- **Founder/CEO:** Bruce McNamara · **CTO:** Bodi · **Legal:** Michael Gamal
- **Base:** Hurghada, Red Sea Governorate, Egypt
- **Grant targets:** ITIDA PDP (EGP 1.6M), ITAC Round 40, UNDP Digital Health
- **Related product:** Seha.io (WhatsApp health triage — pair for UNDP pitch)
- **Branding rule:** Never "AI Solutions Egypt" (deprecated). Always
  "Astra Intelligence Services (Misr)" or "AISE".

---

## OUTPUT CONVENTIONS

All deliverables include the AISE footer:
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
Project · Task Ref · Date Generated
