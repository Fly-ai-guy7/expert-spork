# Phase 5 — Reusability Matrix

Strongest existing implementation of each reusable capability, drawn from the
two confirmed apps. Scores are 1–10. Capabilities with no implementation in
scope are listed at the bottom so the matrix is honest about gaps.

Columns: **Q** quality · **R** reusability · **BC** brand coupling ·
**PC** product coupling.

## Shared application foundation

| Capability | Best source | File/dir | Q | R | BC | PC | Notes / refactor needed | Target package | Priority |
|---|---|---|---|---|---|---|---|---|---|
| App shell + layout containers | Luxor | `frontend/src/App.jsx` (`.app/.container` in `styles.css`) | 7 | 7 | med | low | Extract Header/Footer props (brand, nav, WA link) | `packages/ui` | P1 |
| Suite navigation (multi-page) | RxEgypt | `frontend/nav.js` + `.appnav` in `theme.css` | 7 | 8 | low | low | Already injected + RTL-aware; parameterise links/brand | `packages/ui` | P2 |
| Header / footer | Luxor | `App.jsx` `Header`/`Footer` | 7 | 6 | **high** | low | Brand name/socials/address hard-coded — config-drive | `packages/ui` | P1 |
| Error/loading states | Luxor | `Dashboard()` load/error branches; `.alert ok/err` | 6 | 7 | low | low | Consistent pattern; extract as components | `packages/ui` | P2 |
| Health endpoint idiom | Luxor | `backend/app/main.py` `/healthz` | 8 | 9 | none | none | Copy verbatim into backend starter | template scaffold | P1 |

## Design and UI

| Capability | Best source | File/dir | Q | R | BC | PC | Notes | Target | Priority |
|---|---|---|---|---|---|---|---|---|---|
| **Design tokens (the contract)** | Both (doc: root) | `DESIGN_SYSTEM.md` + two `:root` blocks | 9 | **10** | none (by design) | none | Already a two-brand-proven theme system. Formalise as a package with a validator | `packages/design-tokens` | **P0** |
| Theme system (brand accent aliasing) | Both | `--accent`/`--accent-d` aliasing | 8 | 9 | none | none | The white-label bridge already exists | `packages/design-tokens` | P0 |
| Buttons | Luxor | `.btn` family in `styles.css` (uses tokens) | 7 | 8 | low (`--wa` green aside) | low | Map `.btn-gold`→`.btn-accent` | `packages/ui` | P1 |
| Cards / review cards | Luxor | `.card`, `Reviews()` | 7 | 7 | med (hard-coded review content) | low | Content → config; markup reusable | `packages/ui` | P1 |
| Forms (booking) | Luxor | `DirectBooking()` | 7 | 8 | med | med | Field set is hotel-ish; extract form field primitives + validation states | `packages/forms` | P1 |
| Tables (ops data) | Luxor | Dashboard `.table` | 6 | 7 | low | low | | `packages/ui` | P2 |
| KPI tiles / dashboard | Luxor | Dashboard `kpis` grid | 7 | 8 | low | med | KPI list is data-driven already | `packages/ui` | P1 |
| Status badges | RxEgypt | `.rx-badge`/`.otc-badge` in `theme.css` | 7 | 7 | low | med (Rx semantics) | Generalise to status-badge variants | `packages/ui` | P2 |
| Image galleries / photo slots | Luxor | `.photo .ph-*` placeholder system + `public/img/*.svg` + `IMAGE_CREDITS.md` | 7 | 8 | med | low | Documented drop-in slots = photography-by-config, licensing discipline already in place | `packages/ui` + content schema | P1 |
| Pricing display | Luxor | `roomPrice()` + `.price` | 6 | 7 | low (£ hard-coded) | med | Currency must come from client config | `packages/ui` | P1 |
| Map w/ pins | Luxor | `ExploreMap()` + `MAP_PINS` | 5 | 6 | high (pin data inline) | med | Pins → content files | `packages/ui` | P3 |
| RTL layout support | RxEgypt | `[dir="rtl"]` rules; `dawai-patient.html` | 7 | 8 | none | low | The only RTL implementation in scope — seed of i18n package | `packages/i18n` | P1 |

## Motion

Neither app uses a motion library; Luxor has micro-interactions only (CSS
`transition` on buttons, `transform` on `:active`). **Gap:** page
transitions, shared-layout transitions, reduced-motion handling — all
unimplemented. Do not invent a motion package yet; adopt one (likely Framer
Motion) when the first template that needs it is built, with
`prefers-reduced-motion` support required by QA from day one.

## Product workflows

| Capability | Best source | File/dir | Q | R | BC | PC | Notes | Target | Priority |
|---|---|---|---|---|---|---|---|---|---|
| Booking/enquiry workflow (no-payment) | Luxor | `POST /api/bookings` + `DirectBooking()` + JSON store | 7 | 8 | low | med | The universal "enquiry" primitive for travel/hotel/restaurant | `templates/*` shared workflow | **P0** |
| WhatsApp workflow | Both | Luxor deep links; RxEgypt verification line | 7 | 9 | med | low | Two proven variants (contact + human-verification). Unify as adapter | `packages/integrations` | P1 |
| Deterministic concierge (no-LLM Q&A) | Luxor | `concierge_reply()` in `main.py` + tests | 8 | 8 | low | med | Keyword→ledger matching is domain-configurable (keyword sets + data sources); determinism is tested | `packages/concierge` (or template feature) | P1 |
| Login/registration | RxEgypt | `routes/auth.py` + `security.py` | 8 | 8 | none | low | JWT+bcrypt+roles; registration deliberately patient-only, staff via CLI — good default | `packages/auth` | **P0** |
| Role-based access | RxEgypt | `require_pharmacist`/`require_admin` deps | 8 | 9 | none | low | Rename roles per domain via config | `packages/permissions` | P0 |
| Admin dashboard + metrics | RxEgypt | `routes/admin.py` + `admin.html` | 7 | 7 | low | med | Metrics + audit viewer pattern | `packages/ui` + template | P2 |
| Audit trail | RxEgypt | `audit.py` + `audit_logs` migration + tests | 8 | 9 | none | low | Generic event log; compliance families need it verbatim | `packages/audit` (or auth pkg) | P1 |
| Consent / data-subject rights (PDPL) | RxEgypt | auth routes: consent status/withdraw/export/erasure | 8 | 8 | none | low | Legally load-bearing; reusable for every Egypt-market product | `packages/auth` | P1 |
| Verification queue (human-in-loop approval) | RxEgypt | `orders.py` pending-Rx queue + POS UI | 7 | 7 | low | med | Generalises to any "staff approves risky order" flow | template workflow | P2 |
| Payments (Paymob + mock + HMAC) | RxEgypt | `payments.py` + `routes/payments.py` + tests | 7 | 8 | none | low | Mock-mode-by-default is excellent for QA; live path untested | `packages/integrations` | P1 |
| Content import pipeline (verified data) | RxEgypt | `seed/build_egyptian_drugs.py` + `PROVENANCE.md` | 8 | 8 | none | med | SHA-256-verified reproducible import — the model for `tooling/import-content` | `tooling/import-content` | P1 |

## Shared technical capabilities

| Capability | Best source | Q | R | Notes | Target | Priority |
|---|---|---|---|---|---|---|
| API client w/ auth + demo mode | RxEgypt `frontend/rxegypt-api.js` | 7 | 8 | Per-role tokens, 401/403 handling, demo/live switch via `config.js` — demo mode is a QA gift | `packages/api-client` | P1 |
| Runtime config injection | RxEgypt `frontend/docker-entrypoint.sh` (+`config.js`) | 7 | 9 | Generates config from env at container start — the exact mechanism client instances need | `packages/config` | **P0** |
| Env-driven settings + prod guard | RxEgypt `backend/config.py` | 9 | 9 | Pydantic settings + refuse-to-boot-with-dev-secret validator | backend starter | P0 |
| DB access + migrations | RxEgypt `db.py`/`models.py`/Alembic | 8 | 8 | SQLAlchemy 2 style, SQLite-for-tests trick | backend starter | P1 |
| Form validation (server) | Luxor `BookingIn` / RxEgypt `schemas.py` | 7 | 8 | Pydantic constraints; client-side is native-HTML only | `packages/forms` | P2 |
| Testing patterns | RxEgypt `tests/` (70) + Luxor determinism tests | 8 | 8 | conftest isolated-SQLite fixture; compliance-as-tests | `packages/testing` | P1 |
| CI patterns | both workflows | 8 | 9 | Path-scoped per-app CI in one repo = ready-made monorepo CI idiom | `tooling` | P1 |
| Docker / compose | RxEgypt compose (db+api+web) | 8 | 8 | Full-stack local reference | template scaffold | P1 |
| Smoke testing | Luxor `scripts/smoke_api.sh` | 7 | 8 | Post-deploy health verification | `tooling/production-qa` | P1 |
| i18n (AR/EN + RTL) | RxEgypt `dawai-patient.html` | 6 | 7 | In-page toggle, not a framework; extract string tables | `packages/i18n` | P1 |

## Not implemented anywhere in scope (do not claim these exist)

Analytics, SEO/structured data, image optimisation pipeline, caching layer,
state-management library, file uploads, email sending, search service,
visual-regression testing, Playwright E2E, accessibility tooling, dark mode,
German/Dutch locales, Firebase/Cloud Run deployment configs (Luxor's
Dockerfile is Cloud-Run-*ready* but no `app.yaml`/`cloudbuild.yaml` exists).
These enter the factory as new work, prioritised in `QA_AUTOMATION_PLAN.md`
and `FACTORY_ARCHITECTURE_PROPOSAL.md`.

## Known defects / security considerations attached to reusable candidates

- Luxor booking API: unauthenticated reads expose PII — fix before the
  workflow is templated (`SECURITY_FINDINGS.md` #1).
- Luxor fake `Calendar()`: dummy availability UI must not ship in a template.
- RxEgypt Paymob live path: untested until credentials exist.
- Token contract: no automated guard against drift (convention only).
