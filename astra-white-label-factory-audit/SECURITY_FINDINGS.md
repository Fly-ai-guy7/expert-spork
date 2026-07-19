# Security Findings

No secret values are reproduced anywhere in this audit. Environment-variable
**names** are cited; values were neither read nor printed.

## Repository-wide

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| S0 | **No committed secrets detected.** Pattern scan across all tracked source/config file types found only placeholders (`change-me…`, `dev-only-…`, `ci-secret`). `.env` is git-ignored; only `.env.example` templates committed. | ✅ good | scan run 2026-07-15 | Keep the scan as a CI/QA stage (QA plan stage 17) |

## Luxor Guest House

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| L1 | **Unauthenticated PII exposure:** `GET /api/bookings` and `GET /api/dashboard` return all enquiries (name, email, phone) with no auth. Honestly self-documented in `SECURITY_NOTES.md`, but it remains the top blocker for any public deploy. | High (on public deploy) | `backend/app/main.py` `get_bookings`/`get_dashboard` | Add auth (reuse RxEgypt JWT+role pattern) or network-restrict before go-live; mandatory before the booking workflow is templated |
| L2 | No rate limiting / spam protection on `POST /api/bookings` and `POST /api/concierge` | Medium | same file | Basic rate limit + honeypot field before public launch |
| L3 | CORS: `allow_origin_regex=r"https://.*\.vercel\.app"` with `allow_credentials=True` — any Vercel-hosted site can make credentialed requests | Medium (low while no cookies/auth exist) | `main.py` CORS block | Tighten to the client's exact domains at template-extraction time |
| L4 | Booking store is a plain JSON file containing PII; ephemeral on free Render tier | Medium | `SECURITY_NOTES.md`, `database/bookings.json` | Persistent disk or managed DB before relying on data; never commit a populated store |
| L5 | Real business contact data (WhatsApp number, address) hard-coded in source | Info | `App.jsx`, `contacts.json` | Fine for a single-client MVP; moves to client config in the factory |

## RxEgypt Pilot

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| R1 | **Rx/controlled flags are heuristic, not EDA-verified** — a compliance/patient-safety risk if shipped as-is. Well-documented with a safe-direction bias (ambiguous → Rx) and zero-leak validation, but still unreconciled. | High (compliance) | `seed/PROVENANCE.md`, README warning, CLAUDE.md priority 1 | Reconcile against the EDA register before go-live (already the project's own top task) |
| R2 | Paymob live path (3-step + HMAC callback) untested — only MOCK mode exercised | Medium | `payments.py`, CLAUDE.md status 🟡 | Validate HMAC handling against live Paymob before enabling real payments |
| R3 | Platform Service Agreement (AISE liability shield) unsigned | High (legal, non-code) | CLAUDE.md legal flags #4 | Blocked on Michael Gamal; track outside the repo |
| R4 | JWT secret strength: strong prod guard exists (refuses boot with dev/weak `SECRET_KEY` in production) — **good pattern, adopt factory-wide** | ✅ good | `config.py` `_guard_production` | Port into the factory backend starter |
| R5 | Docs use an example password (`secret123`) for local pharmacist creation | Low | README/CLAUDE.md quick-start | Cosmetic; swap for a `--password <choose-one>` placeholder in docs |
| R6 | `docker-compose.yml` contains dev-only DB credentials (self-labelled) | Low | compose file + README note | Acceptable; keep the "dev-only" labelling |
| R7 | PDPL posture is strong: consent enforced server-side before orders, timestamped consent log, export/withdraw/erasure implemented and tested | ✅ good | auth routes + `test_privacy.py`, `test_auth_consent.py` | Extract as `packages/auth` capability |
| R8 | Audit trail on sensitive actions (Rx verify/reject, fulfil, inventory, consent, erasure) | ✅ good | `audit.py`, `test_audit.py` | Extract with R7 |

## Factory-level security requirements (carried into proposals)

1. Client schema forbids secret values; validator enforces (schema proposal §validation).
2. QA pipeline includes secret-scan, dependency audit, auth-probe, prod-guard boot test (QA plan stage 17).
3. Per-client scoped deploy credentials; QA runner never sees production secrets.
4. PII stores (booking enquiries, patient data) always on durable, access-controlled storage — never JSON files in world-readable deploys.
