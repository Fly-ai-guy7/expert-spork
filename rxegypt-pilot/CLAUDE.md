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
├── frontend/
│   ├── index.html             ← patient-facing app (Experts Pharmacy branded)
│   ├── pharmacy-pos.html      ← pharmacist POS (EAN-13 barcode, stock)
│   ├── dawai-patient.html     ← bilingual AR/EN patient drug app + Health Info Guide
│   └── rxegypt-api.js         ← shared API client (demo + live modes)
├── backend/
│   ├── main.py                ← FastAPI entry point
│   ├── config.py              ← settings (env-driven)
│   ├── db.py                  ← engine + session
│   ├── models.py              ← SQLAlchemy models
│   ├── schemas.py             ← Pydantic schemas
│   ├── security.py            ← JWT + password hashing + role guards
│   ├── routes/
│   │   ├── drugs.py           ← drug search + barcode lookup
│   │   ├── inventory.py       ← stock management
│   │   ├── orders.py          ← orders + Rx gating + WhatsApp verify
│   │   └── auth.py            ← JWT auth + PDPL consent
│   ├── seed/
│   │   ├── drugs_egypt.json   ← Egyptian drug seed data (sample)
│   │   └── seed_drugs.py      ← idempotent seeder
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
| Patient frontend (index.html) | ✅ Scaffolded | Branded; PDPL modal + Rx gating UI |
| Pharmacy POS (pharmacy-pos.html) | ✅ Scaffolded | EAN-13 barcode entry, stock lookup |
| Patient drug app (dawai-patient.html) | ✅ Scaffolded | Bilingual AR/EN, RTL |
| Health Information Guide | ✅ Scaffolded | Renamed from symptom checker; disclaimers; no severity/Rx |
| API client (rxegypt-api.js) | ✅ Scaffolded | Demo mode + live backend switching |
| FastAPI backend | ✅ Scaffolded | JWT auth, drugs, inventory, orders |
| SQLAlchemy models | ✅ Scaffolded | Drug, Inventory, User, Order, OrderItem, Consent |
| Drug seed DB | 🟡 Sample (30 drugs) | Expand toward 250 from EDA/market data |
| Rx drug gating | ✅ Scaffolded | Order → pending_rx_verification + WhatsApp + pharmacist verify |
| PDPL consent flow | ✅ Scaffolded | Bilingual modal; logged to `consents` with timestamp |
| Paymob payment integration | 🟡 Hooks only | Needs live Paymob credentials |
| Alembic migrations | 🔴 Not started | Currently `create_all` via seeder; add Alembic before prod |
| EDA Track & Trace integration | 🔴 Not started | Phase 2 |
| UHI (Universal Health Insurance) API | 🔴 Not started | Phase 3 |

---

## LEGAL FLAGS — DO NOT SHIP WITHOUT THESE

See `legal/RXEG-LEGAL-001.md` for the authoritative list. Summary:

1. **Rx drug gating** — `rx: true` drugs not orderable without pharmacist
   verification (WhatsApp confirmation flow). ✅ scaffolded — review before go-live.
2. **Health Information Guide disclaimers** — bilingual (EN+AR) on every screen,
   no severity ratings, no Rx suggestions. ✅ scaffolded.
3. **PDPL consent** — explicit consent before any data is stored, logged with
   timestamp. ✅ scaffolded.
4. **AISE liability shield** — Platform Service Agreement signed before go-live
   (Michael Gamal action). 🔴 outstanding.

---

## PRIORITY NEXT TASKS

1. Add **Alembic** migrations (replace `create_all`).
2. **Paymob live integration** — swap hooks for live credentials + test.
3. Expand **drug seed DB** toward 250 entries (verify Rx scheduling vs EDA).
4. **Consent withdrawal + data deletion** (PDPL data-subject rights).
5. Backend **tests** (pytest) for Rx gating + consent flows.
6. **EDA Track & Trace** prep — GS1 barcode serialization groundwork.

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
