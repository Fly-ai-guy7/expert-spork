# Phase 3 — Project Registry

Machine-readable version: `project-registry.json`.

**Directories inspected:** `/home/user/expert-spork` (full tree, 100+ files),
`/home/user` (only the repo exists), `/root` (config only — no projects).
**Candidate projects found:** 2 confirmed applications + 1 shared design
contract, all inside one repository. The other 20 named projects from the
brief are registered as `not-observable` (see bottom).

---

## 1. Luxor Guest House MVP — `luxor-guest-house`

### Identity
- **Project ID:** `luxor-guest-house`
- **Display name:** Luxor Guest House — Booking Prototype
- **Path:** `/home/user/expert-spork` (repo root: `frontend/` + `backend/` + `database/`)
- **Product family:** Travel platforms (guest-house direct booking; overlaps hotel/hospitality)
- **Classification:** **canonical** — only implementation, actively maintained, tested, CI-green per `PROJECT_STATUS.md` ("~85% ready for first controlled deployment")

### Technical profile
| Field | Value |
|---|---|
| Language | JavaScript (frontend), Python (backend) |
| Framework | React 18 + Vite 5 / FastAPI |
| Runtime | Node 20–22 / Python 3.11–3.12 |
| Package manager | npm (lockfile committed) |
| Monorepo | Standalone app inside a two-app repo |
| Start | `uvicorn app.main:app --reload --port 8000` + `npm run dev` |
| Build | `npm run build` (Vite) |
| Test | `cd backend && pytest` (11 tests) — **no frontend tests** |
| Lint / typecheck | none configured |
| Expected ports | 8000 (API), 5173 dev / 4173 preview (web), 8080 (nginx container) |
| Docker | Yes — `backend/Dockerfile` (Cloud-Run-ready, `/healthz`), `frontend/Dockerfile` (nginx) |
| CI | `.github/workflows/ci.yml` — pytest + Vite production build, path-scoped |
| Deployment | Render (backend, `render.yaml`) + Vercel (frontend, `vercel.json`); runbook + go-live plan committed |
| Git | `fly-ai-guy7/expert-spork`, branch `main` (audit ran from `claude/astra-factory-discovery-audit-nybtf4`), clean tree |
| Last meaningful change | 2026-06-24 (`faa7200` — replace hotlinked photos with bundled placeholders) |

### Application structure
- **Routes:** SPA, no router — state toggle between guest Home and staff Dashboard (`App.jsx`)
- **Public:** hero, why-stay, experiences, rooms, reviews, map, direct-booking form, concierge chat
- **Auth:** **none** (dashboard and bookings API are open — see SECURITY_FINDINGS)
- **API:** 9 endpoints + `/healthz` (rooms, tours, policies, faq, contacts, bookings GET/POST, dashboard, concierge)
- **Data layer:** JSON ledger files (`backend/app/ledger/*.json`) + append-only `database/bookings.json` (lock-guarded atomic writes)
- **Integrations:** WhatsApp deep links only; deterministic concierge — **no external LLM** (asserted by tests)
- **i18n / RTL:** none (English only)
- **A11y:** minimal (one aria-label); **Testing:** backend only

### Design profile
- Token-driven CSS (`frontend/src/styles.css` `:root`) implementing the AISE
  token contract (`--ink/--muted/--line/--sand/--accent/--accent-d/--radius/--shadow`)
- Playfair Display + Inter; warm gold/sand palette; SVG photo placeholders
  with documented drop-in slots; no component library, no Tailwind, no motion
  library, no dark mode
- Brand coupling: **high in JSX** (hard-coded WhatsApp URL, brand name, reviews,
  experiences, map pins) but **low in data** (rooms/tours/policies/contacts
  already externalised to ledger JSON)

### Quality scores (1–10, evidence-based)
| Dimension | Score | Evidence |
|---|---|---|
| Product completeness | 7 | Full guest funnel + staff dashboard; no payments/availability engine (by design — enquiry model) |
| Code quality | 7 | Clean, small, documented (`main.py` docstrings); no linting configured |
| Architecture | 6 | Sensible 2-tier; JSON file store is a deliberate MVP limit (`PROJECT_STATUS.md` blockers) |
| UI quality | 7 | Coherent hi-fi buyer design, token contract |
| UX quality | 6 | Clear funnel; fake calendar (`Calendar()` renders dummy availability) is a truthfulness risk |
| Responsive | 6 | Media queries present in `styles.css`; untested formally |
| Accessibility | 3 | No semantic audit, emoji icons, contrast unverified |
| Testing | 5 | 11 backend tests incl. concierge determinism; zero frontend tests |
| Security | 4 | No auth on PII endpoints (self-documented in `SECURITY_NOTES.md`) |
| Performance | 7 | Static Vite build, tiny deps (react+react-dom only), SVG assets |
| Reusability | 7 | Ledger-driven content + token contract = strong template genes |
| White-label readiness | 5 | Data externalised; frontend brand hard-coded (see WHITE_LABEL_READINESS) |
| Deployment readiness | 8 | Dockerfiles, render.yaml, vercel.json, runbook, smoke script, CI |
| Documentation | 9 | README, status, testing, security, runbook, go-live plan, design system |

---

## 2. RxEgypt Pilot — `rxegypt-pilot`

### Identity
- **Project ID:** `rxegypt-pilot`
- **Display name:** RxEgypt Pilot — Experts Pharmacy Hurghada
- **Path:** `/home/user/expert-spork/rxegypt-pilot`
- **Product family:** Health and pharmacy platforms (with strong compliance features)
- **Classification:** **canonical** — only implementation; pilot for a real client (Experts Pharmacy)

### Technical profile
| Field | Value |
|---|---|
| Language | Python (backend), vanilla HTML/CSS/JS (frontend, no build step) |
| Framework | FastAPI + SQLAlchemy 2 + Alembic / static pages + shared `rxegypt-api.js` client |
| Runtime | Python 3.11, PostgreSQL 15 (SQLite for tests/CI) |
| Package manager | pip (backend); none (frontend) |
| Monorepo | Standalone app inside the two-app repo |
| Start | `uvicorn main:app --reload --port 8000` + `python -m http.server 3000`; or `docker compose up --build` (db+api+web) |
| Build | none needed (static frontend); Docker images for both tiers |
| Test | `pytest -q` — **70 tests** (Rx gating, payments, PDPL, audit, auth, inventory, config guard); `node test/api.test.js` (JS demo-mode tests) |
| Lint | `ruff check .` (pinned 0.15.8, `ruff.toml`) |
| Expected ports | 8000 (API — **collides with Luxor**), 3000 (web) |
| Docker | Yes — backend + frontend Dockerfiles, `docker-compose.yml` full stack |
| CI | `rxegypt-ci.yml` — ruff + Alembic migrate + seed + pytest + JS checks, path-scoped |
| Deployment | Fly.io (`fly.toml`, release = migrate + seed); frontend → any static host/Cloudflare |
| Git | same repo, clean tree; last meaningful change 2026-06-24 (`3b6da5d` token unification) |

### Application structure
- **Pages:** `index.html` (patient store), `pharmacy-pos.html` (POS + Rx queue + fulfilment), `dawai-patient.html` (bilingual AR/EN drug app + health guide), `admin.html` (metrics + audit viewer); `nav.js` injects suite navigation
- **Auth:** JWT (HS256) + bcrypt; roles patient/pharmacist/admin with dependency guards (`security.py`); registration creates patients only; staff created via CLI
- **Domain:** 24,868-drug Egyptian catalogue (CC0, SHA-256-verified provenance), EAN-13 barcode lookup, Rx gating → `pending_rx_verification` → pharmacist WhatsApp verify, controlled-substance server-side block, inventory, orders, Paymob payments (mock + live+HMAC wired), PDPL consent + data-subject rights (export/withdraw/erasure-by-anonymisation), audit trail, admin metrics
- **i18n / RTL:** **Yes — AR/EN with `[dir="rtl"]` support** (`dawai-patient.html`, `theme.css`)
- **Migrations:** 5 Alembic revisions

### Design profile
- `theme.css` = canonical shared tokens + suite nav; pharmacy green + Rx red
  (`--rx`); implements the AISE token contract; system-ui type; no
  framework/Tailwind/motion; per-page styles cascade on top of shared theme

### Quality scores (1–10)
| Dimension | Score | Evidence |
|---|---|---|
| Product completeness | 8 | Full patient→POS→fulfilment lifecycle; Paymob live untested; EDA/UHI phases pending |
| Code quality | 8 | Ruff-linted, typed settings, clean route/model split |
| Architecture | 8 | Proper layering (config/db/models/schemas/security/routes), migrations, env-driven settings, prod boot guard |
| UI quality | 6 | Functional, token-consistent; static-page aesthetic, not hi-fi |
| UX quality | 6 | Browse-free patient flow, consent at checkout is good; multi-page suite less polished |
| Responsive | 6 | Mobile-first claim; unverified formally |
| Accessibility | 4 | RTL is strong; no broader a11y implementation |
| Testing | 8 | 70 backend tests + JS tests + CI with real migrations/seed |
| Security | 8 | JWT+bcrypt+roles, prod SECRET_KEY guard, HMAC verify, audit log, PDPL rights; see findings |
| Performance | 7 | No-build frontend deliberately fast on mobile; gz-seeded catalogue |
| Reusability | 6 | Auth/audit/consent/API-client patterns are portable; domain is pharmacy-specific |
| White-label readiness | 5 | Config-driven backend; client branding hard-coded in HTML pages |
| Deployment readiness | 8 | Dockerfiles, compose, fly.toml with release migrate+seed, CI |
| Documentation | 9 | README, CLAUDE.md, api-spec, legal framework, provenance doc, weekly updates |

---

## 3. AISE Design-Token Contract — `aise-design-tokens`

- **Path:** `/home/user/expert-spork/DESIGN_SYSTEM.md` + the two `:root` blocks
  (`frontend/src/styles.css`, `rxegypt-pilot/frontend/theme.css`)
- **Family:** Shared infrastructure and component libraries
- **Classification:** canonical (documentation-level shared package; the seed
  of `packages/design-tokens`)

---

## Named projects not present in the audited environment

Registered in `project-registry.json` with `"status": "not-observable"` so the
registry is complete and extendable on the Mac: Atlas Voyage, Voyara
White-Label Travel, Astra Travel Egypt, Luxor Smart Trip Planner*, Astra
Hospitality Loop, Founder OS, Hotel OS Modular Platform, Marina Ember,
Hurghada Restaurant Opportunity Platform, SafePlate, REYEYE Marine SDS,
HealthLoop, EQUALISE, Compound OS, Bruce OS, Dashy, The Hive, Family ELM,
OmniCore AGX, BridgeOS Router, Destination Factory, Tourism Intelligence
Engine, BizBox Hospitality Intelligence.

\* "Luxor Smart Trip Planner" may refer to (or share lineage with) the Luxor
Guest House app in this repo — the guest house app includes tours and a trip
concierge, but is enquiry-based, not a planner. Treated as a **possible
relative, unconfirmed**; do not merge the identities without checking the Mac.
