# Go-Live Plan — from here to live, step by step

_For someone who finds deployment painful. Every step says exactly what to click,
what to paste, and who does it (You vs Claude). Last updated 2026-06-24._

## How we'll work together

- **You** do the clicks in Render / Vercel (I can't log into your accounts).
- **Claude (me)** prepares every config, gives you exact values to paste,
  watches CI, and fixes any build/test failure you hit. Paste me an error and
  I'll turn it around.
- We **ship the smallest thing first** (Luxor) to get one real URL live and
  build confidence, then repeat the pattern for RxEgypt.

## The map (milestones)

```
Phase 0  Accounts ready            ~10 min   (You)
Phase 1  Luxor LIVE  ◀ first win   ~25 min   (You click, I guide)
Phase 2  Luxor hardened            ~30 min   (durable data, email, domain)
Phase 3  RxEgypt LIVE              ~45 min   (needs a database)
Phase 4  Pre-go-live gates         (depends) (Paymob, EDA, legal — not code)
Phase 5  Operate                   ongoing   (backups, rollback, monitoring)
```

## Recommended path: Render + Vercel

Why (given deployment isn't your strong point): the repo is **already
configured** for it (`render.yaml`, `vercel.json`), both connect straight to
GitHub with web UIs, and there's **almost no command line**. Cloud Run and Fly.io
are documented as alternatives at the end — same Dockerfiles — but start here.

---

## Phase 0 — Accounts (~10 min, You)

1. You already have **GitHub** (this repo lives there).
2. Create a **Render** account → https://render.com → "Get Started" → **Sign in
   with GitHub** → authorise access to the `expert-spork` repo.
3. Create a **Vercel** account → https://vercel.com → **Continue with GitHub** →
   authorise the same repo.

That's it. No CLI, no keys.

---

## Phase 1 — Get Luxor LIVE (~25 min) ◀ do this first

### 1A. Backend → Render (the API)

1. Render dashboard → **New +** → **Blueprint**.
2. Pick the `expert-spork` repo. Render reads `render.yaml` and proposes a
   service: **luxor-guest-house-api** (root dir `backend`, Python 3.11.9).
3. Click **Apply**. Wait for the first deploy (≈2–3 min).
4. Copy the URL it gives you, e.g. `https://luxor-guest-house-api.onrender.com`.
5. Test it: open that URL — you should see JSON with `"status": "ok"`. Also try
   `…/healthz` and `…/docs`.

> If the build fails: copy the red log lines and paste them to me. (CI already
> runs this exact build green, so this should "just work.")

### 1B. Frontend → Vercel (the website)

1. Vercel → **Add New… → Project** → import `expert-spork`.
2. Vercel auto-detects the root `vercel.json` (build = `frontend`). Leave the
   build settings as-is.
3. Open **Environment Variables** and add **one**:
   - Name: `VITE_API_URL`
   - Value: your Render URL from step 1A.4, **no trailing slash**
     (e.g. `https://luxor-guest-house-api.onrender.com`)
4. Click **Deploy**. Wait ≈1–2 min. You get a URL like
   `https://expert-spork.vercel.app`.

### 1C. Connect them (CORS)

`*.vercel.app` is already allowed by the backend, so the default Vercel URL works
with **no extra step**. (Only if you later add a custom domain do you set
`ALLOWED_ORIGINS` on Render — see Phase 2.)

### 1D. Prove it works (smoke test)

In this repo (or ask me to run it):

```bash
API=https://luxor-guest-house-api.onrender.com ./scripts/smoke_api.sh
```

Expect all `PASS`. Then open your Vercel URL and check: rooms/tours load, the
concierge replies, a booking submits and shows on the **Dashboard** tab, and the
WhatsApp buttons open `wa.me/201001842081`.

**✅ At this point Luxor is live.** Capture the Vercel URL for your buyer.

> Note: Render's free plan **sleeps** the API after inactivity, so the first
> request after idle takes ~30s to wake. Fine for a demo; Phase 2 covers fixing
> it for real use.

---

## Phase 2 — Harden Luxor for real use (~30 min)

Do these once the demo URL is confirmed.

1. **Durable bookings** (free-tier wipes the JSON file on each redeploy):
   - Easiest: in Render → the API service → **Disks** → add a 1 GB disk mounted
     at `/var/data`. Then **Environment** → add `BOOKINGS_FILE=/var/data/bookings.json`.
     Redeploy. (The commented block in `render.yaml` documents this.)
   - I can switch the store to a managed database instead if you'd rather — say
     the word and I'll wire it.
2. **Real contact email**: give me the address and I'll replace the placeholder
   `info@luxorguesthouse.local` in the ledger + assumptions (1 commit).
3. **Custom domain** (optional): add it in Vercel (Project → Domains), then on
   Render set `ALLOWED_ORIGINS=https://yourdomain.com`.
4. **No-sleep API** (optional): upgrade the Render service off free, or accept the
   cold start for a pilot.

---

## Phase 3 — Get RxEgypt LIVE (~45 min)

RxEgypt needs a **database**, so it's a few more steps. Pattern mirrors Phase 1.

### 3A. Database

- Render → **New + → PostgreSQL** → create (free tier is fine to start). Copy its
  **Internal Database URL**.

### 3B. Backend (Docker web service)

1. Render → **New + → Web Service** → pick `expert-spork`.
2. Settings:
   - **Root Directory:** `rxegypt-pilot/backend`
   - **Runtime:** Docker (Render detects the `Dockerfile`)
   - **Pre-Deploy Command:** `alembic upgrade head && python seed/seed_drugs.py`
     (runs migrations + loads the 24,868-drug catalogue before each release)
3. **Environment variables** (I'll give you final values):
   - `DATABASE_URL` = the Postgres URL from 3A (use the `postgresql+psycopg2://…`
     form — I'll format it for you)
   - `SECRET_KEY` = a long random string. Generate one:
     `python -c "import secrets; print(secrets.token_urlsafe(48))"`
   - `ENVIRONMENT=production`
   - `CORS_ORIGINS=` your RxEgypt frontend URL (set after 3C)
   - `PHARMACIST_WHATSAPP=+20…` (the pharmacy's line)
   - Leave all `PAYMOB_*` **blank** → payments stay in safe **MOCK mode** until
     you have live credentials (Phase 4).
4. Deploy. Check `…/docs` and `…/healthz`-equivalent (`/`).
5. Create a pharmacist login (Render → service → **Shell**):
   `python seed/create_user.py --email pharmacist@experts.eg --password '<pick>' --role pharmacist --name "Head Pharmacist"`

### 3C. Frontend (static)

- The RxEgypt frontend is static HTML. Easiest: Render → **New + → Static Site**
  pointing at `rxegypt-pilot/frontend`, or use its `Dockerfile`. Set the API URL
  via `config.js` / the container's `RXEGYPT_API_URL`. Then set the backend's
  `CORS_ORIGINS` to this frontend URL and redeploy the backend.
- I'll prep the exact config switch for whichever host you pick.

**✅ RxEgypt is live in demo/MOCK-payment mode** — safe to show, not yet taking
real money or dispensing Rx online.

---

## Phase 4 — Pre-go-live gates (not deployment — but required before real users)

These are blocked on **external input**, not on code. Tracked here so nothing is a
surprise:

| Gate | Needed from | Until then |
|---|---|---|
| **Paymob** live credentials + callback URL | Paymob account | Payments run in MOCK mode |
| **EDA reconciliation** of Rx/controlled flags | EDA register data | Flags are heuristic (safe-by-default: ambiguous = Rx) |
| **Barcodes / strengths** in catalogue | GS1/EDA data | Search works; barcode sale limited |
| **AISE Platform Service Agreement** signed | Michael Gamal (legal) | Don't onboard the live pharmacy |

When you have any of these, hand it to me and I'll wire/validate it.

---

## Phase 5 — Operate (ongoing)

- **Rollback:** Render → Deploys → pick a good one → Rollback. Vercel →
  Deployments → previous → Promote to Production.
- **Backups:** enable Postgres backups on Render; export `bookings.json`
  periodically (or move to DB, Phase 2).
- **Monitoring:** watch the Render service logs; `/healthz` is your uptime check.
- **CI:** every push runs tests + build (`.github/workflows/ci.yml` +
  `rxegypt-ci.yml`). Green CI = safe to deploy.

---

## Who does what

| Step | You | Claude |
|---|---|---|
| Create accounts, click Deploy, paste env values | ✅ | — |
| Configs, env value formatting, smoke scripts | — | ✅ |
| Read a build error and fix it | paste it | ✅ |
| Real photos, real email, durable storage, DB swap | provide assets/decision | ✅ wires it |
| Paymob/EDA/legal | provide credentials/data | ✅ integrates |

## One decision for you

Confirm the platform and I'll tailor the exact next clicks:

- **Render + Vercel** — recommended, easiest, repo already configured. _(default)_
- **Google Cloud Run** — you mentioned this; more powerful, more setup
  (gcloud CLI, project, Cloud SQL). Dockerfiles are ready if you want it.
- **Fly.io** — RxEgypt already has `fly.toml`; CLI-based.

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
Portfolio · Go-Live Plan · 2026-06-24
