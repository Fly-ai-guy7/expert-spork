# Deployment & UI/UX Merge Plan

_Portfolio: Luxor Guest House MVP + RxEgypt Pilot · Last updated 2026-06-24_

This plan covers (A) getting both apps production-ready and onto a cloud, and
(B) the UI/UX merge strategy. Both apps currently **pass their full CI locally**
(see "Current state"); the remaining work is operational hardening + deployment,
not bug-fixing.

---

## Current state (verified 2026-06-24)

| App | Backend tests | Lint | Frontend | DB/seed | Container |
|---|---|---|---|---|---|
| **Luxor Guest House** | ✅ 11 pytest | n/a | ✅ Vite build | n/a (JSON store) | ✅ Dockerfile added (API + frontend) |
| **RxEgypt Pilot** | ✅ 70 pytest | ✅ ruff | ✅ JS syntax + unit | ✅ migrate + 24,868 drugs | ✅ Dockerfiles + fly.toml |

No outstanding code errors. What stands between "green" and "in production" is
the gap list in the final section.

---

## A. Deployment

### Recommended target: **Google Cloud Run** (containers), one GCP project

Rationale: both apps are now containerized; Cloud Run gives a single billing /
IAM / logging surface, scales to zero (cheap for a pilot), and is Frankfurt-close
to Egypt (`europe-west3`). The committed Dockerfiles are portable, so Fly.io or
Render remain drop-in alternatives (see "Alternatives").

> Decision still open: confirm Cloud Run vs Render+Vercel vs Fly. The Dockerfiles
> work for all three; only the deploy commands below differ.

#### Services to run

| Service | Image | Notes |
|---|---|---|
| `luxor-api` | `backend/Dockerfile` | FastAPI. Stateless except the JSON booking store → needs durable storage (below). Health: `GET /healthz`. |
| `luxor-web` | `frontend/Dockerfile` | nginx static (port 8080). Build arg `VITE_API_URL` = luxor-api URL. |
| `rxegypt-api` | `rxegypt-pilot/backend/Dockerfile` | FastAPI + Postgres. Run `alembic upgrade head` + seed as a release/job step. Health via `/`. |
| `rxegypt-web` | `rxegypt-pilot/frontend/Dockerfile` | static; `RXEGYPT_API_URL` injected at start. |

#### Cloud Run deploy (per service, illustrative)

```bash
# one-time
gcloud config set project <PROJECT_ID>
gcloud config set run/region europe-west3

# Luxor API
gcloud run deploy luxor-api \
  --source backend \
  --allow-unauthenticated \
  --set-env-vars "ALLOWED_ORIGINS=https://<luxor-web-url>"

# Luxor web (bake the API URL at build)
gcloud run deploy luxor-web \
  --source frontend \
  --allow-unauthenticated \
  --build-arg VITE_API_URL=https://<luxor-api-url>

# RxEgypt API (provision Cloud SQL Postgres first; set DATABASE_URL secret)
gcloud run deploy rxegypt-api --source rxegypt-pilot/backend \
  --set-secrets "SECRET_KEY=rxegypt-secret:latest,DATABASE_URL=rxegypt-db-url:latest" \
  --set-env-vars "ENVIRONMENT=production,API_PREFIX=/api/v1"
# then run migrations+seed as a Cloud Run Job or one-off exec.
```

**Persistence:**
- Luxor bookings are a single JSON file — ephemeral on any scale-to-zero
  container. For the pilot, set `BOOKINGS_FILE` to a mounted GCS bucket (via
  gcsfuse) **or** migrate the two `read_bookings`/`write_bookings` helpers to
  Cloud SQL / Firestore. Recommendation: Firestore (tiny schema, zero ops).
- RxEgypt requires **Cloud SQL for PostgreSQL**; never run on container-local
  storage.

**Secrets:** use Google Secret Manager for `SECRET_KEY`, `DATABASE_URL`,
`PAYMOB_API_KEY`, `PHARMACIST_WHATSAPP`. Nothing secret in the repo (verified).

#### Alternatives (no code change — same Dockerfiles)

- **Render + Vercel** — already configured for Luxor (`render.yaml`, `vercel.json`).
  Fastest path to a Luxor URL *today*; RxEgypt would need its own Render services.
- **Fly.io** — RxEgypt already ships `fly.toml` (Frankfurt). Extend to Luxor with
  a `fly launch` from `backend/`.

### Deployment sequence (today)

1. Pick the target (Cloud Run recommended; Render+Vercel is the fastest for Luxor).
2. Deploy `luxor-api` → capture URL → deploy `luxor-web` with that URL.
3. `API=<luxor-api-url> ./scripts/smoke_api.sh` → expect all PASS.
4. Provision Postgres → deploy `rxegypt-api` → run migrate+seed → deploy `rxegypt-web`.
5. Set CORS on each API to its web origin.
6. Capture both live URLs for the buyer/grant demo.

---

## B. UI/UX merge

> The exact scope of "UI/UX merge" is unconfirmed. Below are the three
> interpretations I can see, with a recommended path. Tell me which and I'll
> execute it.

### Option 1 — Unify RxEgypt's pages into one shell *(recommended first step)*

RxEgypt is currently four standalone HTML pages (`index`, `pharmacy-pos`,
`dawai-patient`, `admin`) that already share `rxegypt-api.js` + `config.js` but
not a common header/nav/theme. Merge work:

- Extract a shared CSS theme (tokens: colours, type, spacing, RTL rules) into one
  stylesheet imported by all pages.
- Add a consistent top bar + role-aware nav (patient / pharmacist / admin).
- Normalise the bilingual AR/EN + RTL toggle into one shared component.
- Keep pages separate (no build step) but visually unified — low risk, high polish.

Effort: ~half a day. No backend change. Directly improves the demo.

### Option 2 — One AISE design system across both products

Bring Luxor (React) and RxEgypt (vanilla) under shared design tokens + brand
(AISE). Practical version: a single `tokens.css` (colours, type scale, radius,
shadows) consumed by both, plus a shared logo/footer. Full component-library
unification across React + vanilla is **not** a one-day job — recommend tokens +
brand now, component parity later.

### Option 3 — Merge an external design handoff

If there's a Figma file or designer branch, point me at it and I'll implement the
screens against the existing components. (Figma MCP tooling is available in this
session.) Needs the source link.

### Recommendation

Do **Option 1** today (contained, visible win on the regulated app), adopt the
**Option 2 token layer** as the shared foundation, and reserve Option 3 for when a
concrete design source exists.

---

## Production-readiness gap list

| # | App | Gap | Today-doable? | Type |
|---|---|---|---|---|
| 1 | Luxor | Durable booking storage (Firestore / Cloud SQL / GCS) | ⚠️ code change (~2h) | infra+code |
| 2 | Luxor | Real contact email (replace `info@luxorguesthouse.local`) | ✅ data edit | data |
| 3 | Luxor | Auth on staff dashboard / `GET /api/bookings` (currently open) | ⚠️ product decision | security |
| 4 | RxEgypt | Reconcile heuristic `rx`/`controlled` flags vs EDA register | ❌ needs EDA data | compliance |
| 5 | RxEgypt | Paymob live credentials + HMAC callback validation | ❌ needs credentials | payments |
| 6 | RxEgypt | Barcodes + strengths in catalogue (GS1/EDA) | ❌ needs data source | data |
| 7 | RxEgypt | AISE Platform Service Agreement signed (liability shield) | ❌ legal/human | legal |
| 8 | Both | Provision Postgres (RxEgypt) / chosen store (Luxor) on cloud | ✅ once target picked | infra |

Legend: ✅ can finish today · ⚠️ doable today with a decision · ❌ blocked on
external input (credentials, data, legal, human).

**Net:** items 2 and (with your go-ahead) 1 and 3 are finishable today on the code
side. 4–7 are genuinely blocked on external inputs — they are not code bugs and
cannot be "completed" by me without that input.

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
Portfolio · Deployment & UI/UX Plan · 2026-06-24
