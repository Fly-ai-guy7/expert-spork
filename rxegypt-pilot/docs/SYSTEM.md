# RxEgypt Pilot — System Documentation

**Project:** RxEgypt — B2B pharmacy management & patient platform
**Pilot client:** Experts Pharmacy, Al Ahyaa, Hurghada, Red Sea Governorate, Egypt
**Built by:** Astra Intelligence Services (Misr) — AISE
**Status:** Pilot build complete (merged) · pre-go-live

> This is the single authoritative overview of the whole system. Deep-dives live
> in [`docs/api-spec.md`](api-spec.md), [`backend/seed/PROVENANCE.md`](../backend/seed/PROVENANCE.md),
> [`legal/RXEG-LEGAL-001.md`](../legal/RXEG-LEGAL-001.md), and [`CLAUDE.md`](../CLAUDE.md).

---

## 1. What it is

RxEgypt lets patients search a real Egyptian medicine catalogue, place orders, and
pay, while pharmacists verify prescriptions, manage stock, and fulfil orders, and an
admin oversees activity. It is **regulation-first**: Egyptian pharmacy and data-
protection rules are enforced in code, not just documented.

Three audiences, three frontends, one API:

| Audience | Surface | Key jobs |
|---|---|---|
| Patient | `index.html` (+ `dawai-patient.html` lookup) | browse, consent, order, pay, view orders, manage data |
| Pharmacist | `pharmacy-pos.html` | barcode sale, stock, Rx-verification queue, fulfillment, low-stock |
| Admin | `admin.html` | metrics + audit trail |

---

## 2. Tech stack

- **Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 15 (SQLite for dev/tests)
- **Auth:** JWT (python-jose) · bcrypt password hashing
- **Payments:** Paymob (Egypt) with a credential-free MOCK mode
- **Frontend:** Vanilla HTML/CSS/JS (no build step; fast on mobile; AR/EN + RTL)
- **Deploy:** Docker · Fly.io · docker-compose (local full stack)
- **CI:** GitHub Actions (ruff + pytest + frontend JS tests)

---

## 3. Repository layout

```
rxegypt-pilot/
├── CLAUDE.md                  project guide / status
├── README.md                  setup + deploy
├── docker-compose.yml         local full stack (db + backend + frontend)
├── docs/
│   ├── SYSTEM.md              ← this file
│   └── api-spec.md            endpoint reference
├── legal/
│   ├── RXEG-LEGAL-001.md      Egyptian compliance framework
│   └── RXEG-GRANT-001.md      grant funding strategy
├── frontend/
│   ├── index.html             patient app
│   ├── pharmacy-pos.html      pharmacist POS
│   ├── admin.html             admin oversight
│   ├── dawai-patient.html     bilingual drug lookup + Health Information Guide
│   ├── rxegypt-api.js         shared API client (demo + live)
│   ├── config.js              demo ↔ live switch
│   ├── Dockerfile             static server (injects config from env)
│   └── docker-entrypoint.sh
└── backend/
    ├── main.py                FastAPI app + router wiring + CORS
    ├── config.py              env settings + production secret guard
    ├── db.py                  engine + session
    ├── models.py              SQLAlchemy models
    ├── schemas.py             Pydantic schemas
    ├── security.py            JWT, hashing, role guards
    ├── payments.py            Paymob client + MOCK mode + HMAC verify
    ├── audit.py               audit-log helper
    ├── routes/                auth, drugs, inventory, orders, payments, audit, admin
    ├── seed/                  build_egyptian_drugs.py, drugs_egypt.json.gz, seed_drugs.py,
    │                          create_user.py, PROVENANCE.md
    ├── migrations/            Alembic (5 revisions)
    ├── tests/                 pytest suite (70 tests)
    ├── Dockerfile · fly.toml · requirements.txt · ruff.toml
```

---

## 4. Architecture & request flow

```
Browser (index / pos / admin / dawai)
   │  fetch + JWT Bearer (per-page token key)
   ▼
FastAPI (/api/v1)  ──►  routes  ──►  SQLAlchemy models  ──►  PostgreSQL
   │                       │
   │                       ├─ security.py  (JWT decode, role guards)
   │                       ├─ payments.py  (Paymob / mock)
   │                       └─ audit.py     (audit_logs)
```

- Single API prefix `/api/v1`; routers: `auth`, `drugs`, `inventory`, `orders`,
  `payments`, `audit`, `admin`.
- CORS allow-list from `CORS_ORIGINS` (default `http://localhost:3000`).
- The frontend is **demo-capable**: with no `RXEGYPT_API_URL` set it runs entirely
  on bundled sample data; set it (via `config.js`) to go live.

---

## 5. Data model

| Table | Purpose | Notable fields |
|---|---|---|
| `users` | accounts | `email`, `hashed_password`, `role` (patient/pharmacist/admin), `deleted_at` (erasure) |
| `drugs` | catalogue | `name_en/ar`, `generic`, `category`, `manufacturer`, `barcode`, `price_egp`, `rx`, `controlled`, `rx_source` |
| `inventory` | stock | `drug_id` (unique), `quantity`, `reorder_level`, `updated_at` |
| `orders` | patient orders | `user_id`, `status`, `requires_rx_verification`, `rx_verified_by`, `total_egp`, `paymob_order_id` |
| `order_items` | order lines | `order_id`, `drug_id`, `quantity`, `unit_price_egp` |
| `consents` | PDPL consent log | `user_id`, `purpose`, `granted`, `policy_version`, `created_at` |
| `audit_logs` | accountability | `actor_email`, `action`, `target`, `detail`, `created_at` |

Schema is managed by **Alembic** (5 migrations). `seed/seed_drugs.py` bulk-loads the
catalogue; `seed/create_user.py` provisions pharmacist/admin accounts.

---

## 6. Order lifecycle (state machine)

```
            create order (POST /orders)
                     │
        any rx item? ├── yes ─► pending_rx_verification ──(pharmacist verify)──► pending_payment
                     │                     └──────────────(pharmacist reject)──► cancelled
                     └── no  ─────────────────────────────────────────────────► pending_payment
                                                   │
                                       pay + settle │ (Paymob / mock)
                                                   ▼
                                                 paid ──(pharmacist fulfill: decrements stock)──► fulfilled
```

- **Controlled** drugs are rejected at order creation (never enter the flow).
- OTC-only orders skip straight to `pending_payment`.
- Fulfilment decrements `inventory.quantity` (clamped at 0) for tracked drugs.

---

## 7. Roles & auth

- JWT bearer tokens (8h), issued by `POST /api/v1/auth/login` (OAuth2 password form).
- Roles: **patient** (self-register), **pharmacist**, **admin** (created via
  `seed/create_user.py` — `/auth/register` only ever makes patients).
- Guards: `get_current_user`, `require_pharmacist`, `require_admin`. Deleted accounts
  are rejected at login and on every request.
- Frontend namespaces the token per page (`rxegypt_token`, `rxegypt_token_pharmacist`,
  `rxegypt_token_admin`) so patient/pharmacist/admin sessions don't collide.

---

## 8. Legal & compliance controls

All enforced **server-side** (see [`legal/RXEG-LEGAL-001.md`](../legal/RXEG-LEGAL-001.md)):

1. **Rx gating** — `rx:true` orders go to `pending_rx_verification`; a pharmacist must
   verify before payment. Patient is routed to a WhatsApp confirmation link.
2. **Controlled substances** — `controlled:true` items cannot be ordered online (400);
   in-pharmacy dispensing only. UI hides the Add button / shows "🔒 In-pharmacy only".
3. **PDPL consent (Law 151/2020)** — `POST /orders` requires a granted `Consent`
   record (403 otherwise); the frontend modal alone is not relied upon.
4. **PDPL data-subject rights** — consent status & withdrawal, data export (portability),
   and account erasure (anonymize PII + block login; retain de-identified orders).
5. **Health Information Guide** — bilingual EN/AR disclaimers on every screen; no
   diagnosis, no severity ratings, no Rx suggestions.
6. **Audit trail** — `audit_logs` records who/what/when for Rx verify/reject,
   fulfillment, inventory changes, consent grant/withdraw, and account erasure;
   readable by admins at `GET /audit`.

> ⚠️ The `rx` and `controlled` flags are **heuristics** derived from the dataset and
> **must be reconciled against the official EDA register before go-live.**

---

## 9. Drug catalogue & provenance

- Source: [`karem505/egyptian-drug-database`](https://github.com/karem505/egyptian-drug-database)
  — **24,868** medicines, **CC0-1.0**. Not an official EDA feed.
- `seed/build_egyptian_drugs.py` downloads it, **verifies SHA-256**, maps it to the
  `Drug` schema, derives `rx`/`controlled`, and writes `drugs_egypt.json.gz` (~1.1 MB)
  + `PROVENANCE.md`.
- Derivation: hard-Rx list wins → OTC allow-list → else Rx. Result **14,907 Rx /
  9,961 OTC**, **311 controlled**, validated with zero antibiotic/cardio/antidiabetic/
  steroid leaks into OTC.
- Gaps: no barcodes or strengths in the source (add from EDA/GS1).

---

## 10. Payments (Paymob)

- `POST /orders/{id}/pay` creates a payment intent.
- **MOCK mode** (no `PAYMOB_API_KEY`): returns `mock:true`; settled via
  `POST /payments/mock/confirm` — the full lifecycle is testable with no credentials.
- **LIVE mode**: 3-step Paymob Accept flow (auth → order → payment key) returns a
  checkout URL; the processed-transaction callback (`/payments/paymob/callback`) is
  **HMAC-SHA512 verified** and marks the order `paid`.
- ⚠️ The live path is wired but **unverified** — validate field names + HMAC ordering
  against current Paymob docs and register the callback URL before go-live.

---

## 11. Frontend surfaces

- **`index.html`** — patient: browse-free; login/register + PDPL consent required at
  checkout; Rx → WhatsApp, OTC → payment modal; "My orders" (pay later); "Privacy"
  (export / withdraw / delete).
- **`pharmacy-pos.html`** — pharmacist: barcode sale, stock update, Rx-verification
  queue (approve/reject), fulfillment queue (decrements stock), low-stock list.
- **`admin.html`** — metric cards (orders by status, active patients, low-stock) +
  audit-trail viewer with action filter.
- **`dawai-patient.html`** — bilingual drug lookup + Health Information Guide.
- **`config.js`** sets the backend URL (demo ↔ live); **`rxegypt-api.js`** is the
  shared client with full demo parity for every endpoint.

---

## 12. Design system (tokens)

The UI uses a consistent token set (defined in each page's CSS; basis for the Figma build):

| Token | Value | Use |
|---|---|---|
| `--green` | `#1f7a4d` | primary actions, headers |
| `--green-d` | `#14573a` | headings, POS header |
| `--sand` | `#f6f4ee` | app background |
| `--ink` | `#1c2421` | body text |
| `--rx` | `#b3261e` | Rx / controlled / errors |
| OTC badge | `#e6f2eb` on `--green-d` | non-prescription tag |
| radius | 8–12px | inputs, cards, modals |
| font | system-ui / Segoe UI / Tahoma / Cairo | EN + AR |

Components: primary/ghost buttons, Rx / OTC / 🔒 Controlled badges, drug card, modal
shell, form inputs, status pills. (A native Figma file of these is pending editor-seat
access.)

---

## 13. Configuration (env vars)

| Var | Default | Notes |
|---|---|---|
| `DATABASE_URL` | local Postgres | SQLite used in tests/CI |
| `SECRET_KEY` | dev default | **must be strong in production** (boot guard) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 480 | JWT lifetime |
| `CORS_ORIGINS` | `http://localhost:3000` | comma-separated |
| `PHARMACIST_WHATSAPP` | `+20` | Rx confirmation line |
| `PAYMOB_API_KEY` / `_INTEGRATION_ID` / `_IFRAME_ID` / `_HMAC_SECRET` | empty | empty ⇒ MOCK payments |
| `ENVIRONMENT` | `development` | `production` triggers the secret guard |

---

## 14. Local development

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python seed/build_egyptian_drugs.py     # fetch + verify catalogue
python seed/seed_drugs.py               # bulk load
python seed/create_user.py --email pharmacist@experts.eg --password secret123 --role pharmacist
uvicorn main:app --reload --port 8000   # → /docs

# Frontend (separate shell)
cd frontend && python -m http.server 3000   # edit config.js to point at :8000 for live mode

# Or the whole stack:
docker compose up --build
```

---

## 15. Testing & CI

- **70 pytest tests** (in-memory SQLite): Rx gating + queue, fulfillment queue,
  payments + stock decrement, order compliance (consent/controlled), PDPL rights,
  audit + admin metrics, auth, inventory, drugs, Rx derivation, config guard.
- **ruff** lint (clean) and **frontend JS unit tests** (`frontend/test/api.test.js`).
- **GitHub Actions** (`.github/workflows/rxegypt-ci.yml`, path-scoped to `rxegypt-pilot/**`)
  runs lint + backend tests + frontend tests on every push/PR.

---

## 16. Deployment

- **Backend image** (`backend/Dockerfile`) → Fly.io via `backend/fly.toml`; the release
  step runs `alembic upgrade head` + idempotent seed.
- **Frontend image** (`frontend/Dockerfile`) serves the static files and writes
  `config.js` from `RXEGYPT_API_URL` at startup.
- **`docker-compose.yml`** brings up Postgres + backend (migrate→seed→serve) + frontend
  for local full-stack runs.

---

## 17. Go-live checklist (outstanding — external)

- [ ] Reconcile `rx` + `controlled` heuristics against the **EDA register**.
- [ ] **Paymob** live credentials; validate callback fields + HMAC; register callback URL.
- [ ] Add **barcodes + strengths** to the catalogue (EDA/GS1).
- [ ] **Retention schedule** sign-off (drives order/consent retention).
- [ ] Signed AISE ↔ Experts Pharmacy **Platform Service Agreement** (Michael Gamal).
- [ ] Editor-seat Figma file of the design system + screens (pending access).
- [ ] Phase 2: EDA Track & Trace (GS1 serialization). Phase 3: UHI integration.

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
RxEgypt Pilot · docs/SYSTEM.md · Generated 2026-06-15
