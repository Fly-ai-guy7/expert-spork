# Luxor Guest House — Booking Prototype

A deployable MVP for **Luxor Guest House**, a Nile-side guest house on the West
Bank of Luxor, Egypt. Guests can browse rooms and tours, chat with a concierge,
and send a booking enquiry. Staff get a lightweight operations dashboard.

- **Frontend:** React + Vite
- **Backend:** FastAPI (Python)
- **Data:** JSON "ledger" files (rooms, tours, policies, FAQ, contacts) + a JSON
  booking store
- **Deployment:** Vercel (frontend) + Render (backend)

**Project docs:** [`PROJECT_STATUS.md`](PROJECT_STATUS.md) ·
[`TESTING.md`](TESTING.md) · [`SECURITY_NOTES.md`](SECURITY_NOTES.md) ·
[`NEXT_ACTIONS.md`](NEXT_ACTIONS.md) · [`DEPLOYMENT_RUNBOOK.md`](DEPLOYMENT_RUNBOOK.md)

> Property: Luxor Guest House · West Bank, Albairat, Alramla, West Bank, 85111
> Luxor, Egypt · WhatsApp **+20 100 184 2081** · Booking.com **9.0** (470 reviews)
> · Breakfast included · No prepayment · No credit card needed.

---

## Repository structure

```
.
├── README.md
├── DEPLOYMENT_RUNBOOK.md
├── render.yaml                 # Render blueprint for the backend
├── frontend/                   # React + Vite app (deploy to Vercel)
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   ├── .env.example
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
├── backend/                    # FastAPI app (deploy to Render)
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py
│       └── ledger/             # Source-of-truth JSON data
│           ├── rooms.json
│           ├── tours.json
│           ├── policies.json
│           ├── faq.json
│           ├── contacts.json
│           └── assumptions.json
└── database/
    └── bookings.json           # Booking enquiries are appended here
```

## API endpoints

| Method | Path               | Purpose                                   |
| ------ | ------------------ | ----------------------------------------- |
| GET    | `/`                | Service info + endpoint list              |
| GET    | `/api/rooms`       | All rooms                                 |
| GET    | `/api/tours`       | All tours                                 |
| GET    | `/api/policies`    | Booking / stay policies                   |
| GET    | `/api/faq`         | Frequently asked questions                |
| GET    | `/api/contacts`    | Contact + rating info                     |
| GET    | `/api/bookings`    | List booking enquiries                    |
| POST   | `/api/bookings`    | Create a booking enquiry (saved to JSON)  |
| GET    | `/api/dashboard`   | KPIs + recent enquiries + rooms/tours     |
| POST   | `/api/concierge`   | Concierge answer from local ledger data   |

Interactive API docs are available at `/docs` when the backend is running.

---

## Run locally

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now at <http://localhost:8000> (docs at `/docs`).

### 2. Frontend (React + Vite)

In a second terminal:

```bash
cd frontend
cp .env.example .env             # VITE_API_URL defaults to http://localhost:8000
npm install
npm run dev
```

Open the URL Vite prints (default <http://localhost:5173>). Toggle between the
guest **Home** page and the staff **Dashboard** from the top navigation.

### Build the frontend for production

```bash
cd frontend
npm run build        # outputs to frontend/dist
npm run preview      # optional local preview of the build
```

---

## Configuration

### Frontend (`frontend/.env`)

| Variable       | Description                              | Example                               |
| -------------- | ---------------------------------------- | ------------------------------------- |
| `VITE_API_URL` | Base URL of the backend (no trailing /)  | `https://luxor-guest-house-api.onrender.com` |

### Backend (`backend/.env`)

| Variable          | Description                                                        |
| ----------------- | ----------------------------------------------------------------- |
| `ALLOWED_ORIGINS` | Comma-separated extra CORS origins (your frontend URL).           |
| `BOOKINGS_FILE`   | Optional path override for the booking store JSON file.           |

CORS already allows `localhost:5173/3000` and any `*.vercel.app` domain out of
the box; use `ALLOWED_ORIGINS` to add a custom production domain.

---

## Concierge

The concierge (`POST /api/concierge`) is deterministic and answers purely from
the local ledger files — rooms, tours, policies, FAQ and contacts. It performs
keyword matching and composes a reply with the relevant data and a WhatsApp
link. No external LLM or third-party service is called.

## Notes & assumptions

Key assumptions (placeholder email, reference pricing, inferred policies,
ephemeral storage on the free Render plan, etc.) are documented in
[`backend/app/ledger/assumptions.json`](backend/app/ledger/assumptions.json).

## Deployment

See [`DEPLOYMENT_RUNBOOK.md`](DEPLOYMENT_RUNBOOK.md) for step-by-step Vercel +
Render instructions.
