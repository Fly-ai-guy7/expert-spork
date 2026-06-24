# Next Actions — Luxor Guest House MVP

## Immediate deployment actions

1. **Deploy backend to Render** via the `render.yaml` blueprint (root dir
   `backend/`). Verify `/` and `/docs`, then copy the service URL.
2. **Deploy frontend to Vercel** (root dir `frontend/`, Vite preset). Set
   `VITE_API_URL` to the Render URL (no trailing slash).
3. **Smoke test** the live API: `API=<render-url> ./scripts/smoke_api.sh`.
4. **Verify in-browser:** rooms/tours/concierge load, a booking submits and
   appears on the Dashboard, WhatsApp buttons open `wa.me/201001842081`.
5. **Capture the live demo URL** for the buyer.

## Post-deployment improvements

- Replace placeholder email `info@luxorguesthouse.local` with a real mailbox.
- Review and confirm/replace every item in
  `backend/app/ledger/assumptions.json` (reference pricing, inferred policies).
- Add basic rate limiting / spam protection to `POST /api/bookings`.
- Put the staff Dashboard / `GET /api/bookings` behind auth before any public
  launch (currently unauthenticated — see `SECURITY_NOTES.md`).
- Optional: add a lightweight email/WhatsApp notification when an enquiry
  arrives.

## Durable storage recommendation

The JSON booking store is ephemeral on Render's free plan. Before relying on
enquiries persisting, pick one:

- **Quickest:** attach a Render persistent disk and set
  `BOOKINGS_FILE=/var/data/bookings.json` (see the commented block in
  `render.yaml`).
- **More robust:** migrate bookings to a managed database (e.g. Render
  PostgreSQL / Supabase). Keep the same `BookingIn` schema; swap the
  `read_bookings`/`write_bookings` helpers for DB calls.

## Repo rename / migration recommendation

This repository (`expert-spork`) currently hosts **three** lineages: the active
Luxor Guest House MVP (root), the `rxegypt-pilot/` pharmacy project, and stale
PRs (#1–6) for an abandoned legal-sim codebase. To reduce confusion:

- **Recommended:** split the Luxor MVP into its own repository named
  `luxor-guest-house-prototype` (or `luxor-guest-house-mvp`) — the backend
  already references that path name. This gives clean CI, deploy config, and
  issue tracking per product.
- Move `rxegypt-pilot/` to its own repo as well (it already has independent CI,
  Docker, and Fly.io config).
- Close or rebase the stale PRs #1–6, which target code no longer present on
  `main`.
