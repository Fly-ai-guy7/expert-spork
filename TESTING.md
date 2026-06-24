# Testing — Luxor Guest House MVP

## Backend (pytest)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

The suite (`backend/tests/test_api.py`) covers all API endpoints. Booking tests
are **isolated**: a temporary `BOOKINGS_FILE` is set before the app is imported,
so they never mutate `database/bookings.json`.

Covered:

- `GET /` — service status + endpoint list
- `GET /api/rooms`, `/api/tours`, `/api/faq` — non-empty lists
- `GET /api/policies`, `/api/contacts` — valid structured data
- `GET /api/dashboard` — KPIs
- `POST /api/concierge` — deterministic, ledger-backed reply
- `POST /api/bookings` — creates a booking in an isolated temp file
- `GET /api/bookings` — returns the created test booking

## Frontend (build)

```bash
cd frontend
npm install        # CI uses: npm ci
npm run build      # outputs to frontend/dist
npm run preview    # optional local preview of the build
```

A green `npm run build` is the frontend's required check (no unit-test suite —
the app is intentionally light).

## Smoke test (local or live)

Run against any running backend (no `jq` needed):

```bash
# Local
cd backend && uvicorn app.main:app --port 8000 &
API=http://localhost:8000 ../scripts/smoke_api.sh

# Live
API=https://luxor-guest-house-api.onrender.com ./scripts/smoke_api.sh
```

It checks `/`, `/api/rooms`, `/api/tours`, `/api/dashboard`, `/api/concierge`,
and a `POST /api/bookings`, exiting non-zero on the first failure.

## Production smoke-test checklist

- [ ] Backend healthy at `/` and `/docs`.
- [ ] `./scripts/smoke_api.sh` passes against the live API.
- [ ] Frontend loads live rooms, tours and concierge replies.
- [ ] Booking enquiry submits and appears on the Dashboard tab.
- [ ] WhatsApp buttons open `https://wa.me/201001842081`.
- [ ] `VITE_API_URL` points at the production backend (no trailing slash).

## Continuous integration

`.github/workflows/ci.yml` runs on pull requests and pushes to `main` that touch
`backend/`, `frontend/`, or the workflow itself:

- **backend** job — Python 3.12, install deps, `pytest`.
- **frontend** job — Node 20, `npm ci`, `npm run build`.
