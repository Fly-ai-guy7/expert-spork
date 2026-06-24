# Project Status — Luxor Guest House MVP

_Last updated: 2026-06-24_

## Current stack

- **Frontend:** React + Vite (`frontend/`) — single-page app (guest Home + staff Dashboard).
- **Backend:** FastAPI (`backend/`) — JSON "ledger" data + JSON booking store.
- **Data:** `backend/app/ledger/*.json` (rooms, tours, policies, FAQ, contacts, assumptions); booking enquiries appended to `database/bookings.json`.
- **Concierge:** deterministic, ledger-backed keyword matcher. **No external LLM or third-party calls.**

## Runnable services

| Service | Command | Verified |
|---|---|---|
| Backend (FastAPI) | `cd backend && uvicorn app.main:app --reload --port 8000` | ✅ imports, 9 routes live |
| Frontend (Vite dev) | `cd frontend && npm install && npm run dev` | ✅ |
| Frontend (prod build) | `cd frontend && npm run build` | ✅ build green |
| Backend tests | `cd backend && pytest` | ✅ 10 passed |

## Deployment targets

- **Backend → Render** (blueprint: `render.yaml`, root dir `backend/`).
- **Frontend → Vercel** (root dir `frontend/`, Vite preset; root `vercel.json` present).
- See `DEPLOYMENT_RUNBOOK.md` for the step-by-step procedure.

## Readiness

**~85% ready for a first controlled deployment.** The app builds, runs, is
tested, and has CI + a smoke-test script. Remaining items are operational
(durable storage, real contact email) rather than code blockers.

## Critical blockers

- **None blocking a demo deploy.** The app runs without the backend (frontend
  degrades gracefully to bundled data).
- **Before relying on booking data:** Render's free filesystem is ephemeral —
  enquiries in `database/bookings.json` reset on redeploy. Attach a persistent
  disk (`BOOKINGS_FILE=/var/data/bookings.json`) or move to a managed DB.
- **Before go-live:** replace placeholder email `info@luxorguesthouse.local`
  with a real mailbox; review `backend/app/ledger/assumptions.json`.

## Recommended next deployment action

1. Deploy the backend to Render via the blueprint; capture its URL.
2. Deploy the frontend to Vercel with `VITE_API_URL` = the Render URL.
3. Run `API=<render-url> ./scripts/smoke_api.sh`.
4. Capture the live demo URL and review the go-live checklist in the runbook.
