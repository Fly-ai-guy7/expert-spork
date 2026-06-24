# Security Notes — Luxor Guest House MVP

## Secret handling

- **No secrets are committed.** The app needs none to run: the concierge is
  deterministic and ledger-backed, and there are no third-party API keys.
- Configuration is via environment variables only (`VITE_API_URL`,
  `ALLOWED_ORIGINS`, `BOOKINGS_FILE`). `.env` files are git-ignored; commit only
  the `.env.example` templates.
- Do **not** commit API keys, tokens, private notes, valuations, strategy
  documents, or any client-sensitive information.

## No external LLM

The concierge (`POST /api/concierge`) performs **deterministic keyword matching**
over the local JSON ledger (rooms, tours, policies, FAQ, contacts) and composes a
reply with a WhatsApp link. **No external LLM or third-party service is called.**
Keep it this way — it bounds the data surface and keeps replies reproducible
(the test suite asserts determinism).

## CORS

Configured in `backend/app/main.py`:

- Localhost dev origins (`5173`/`3000`) are allowed by default.
- Any `https://*.vercel.app` origin is allowed via regex (covers Vercel
  preview + production).
- A **custom** production domain must be added via `ALLOWED_ORIGINS`
  (comma-separated).
- `allow_credentials=True` with `allow_methods/headers=["*"]`. If credentialed
  requests are ever combined with a wildcard origin, tighten this — but the
  current setup uses an explicit list + a scoped regex, not a wildcard.

## Booking-data persistence limitations

- Enquiries are appended to a JSON file (`database/bookings.json`, or the
  `BOOKINGS_FILE` override). Writes are lock-guarded and atomic (temp file +
  replace) but this is a **single-file store, not a database**.
- On Render's free plan the filesystem is **ephemeral** — booking data resets on
  every redeploy/restart. Attach a persistent disk and set
  `BOOKINGS_FILE=/var/data/bookings.json`, or migrate to a managed DB before
  relying on enquiries persisting.
- The booking store may contain personal data (name, email, phone). Treat it as
  PII: restrict access, and do not commit a populated `bookings.json`.

## Public / private deployment cautions

- The API has **no authentication**. `GET /api/bookings` and `GET /api/dashboard`
  expose all submitted enquiries (including PII). Before a public launch, place
  the staff Dashboard / bookings endpoints behind auth or a private network, or
  restrict them to trusted origins.
- `POST /api/bookings` and `POST /api/concierge` are unauthenticated and
  unrate-limited. For a public demo this is acceptable; for production add basic
  rate limiting / spam protection.
- Keep interactive docs (`/docs`) in mind when deciding what is publicly
  reachable.
