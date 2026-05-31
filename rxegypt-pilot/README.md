# RxEgypt Pilot — Experts Pharmacy Hurghada

B2B SaaS pharmacy management + patient-facing platform.
Built by **Astra Intelligence Services (Misr) — AISE**.
Pilot client: **Experts Pharmacy**, Al Ahyaa, Red Sea Governorate, Egypt.

> ⚖️ Regulation-first build. Prescription (Rx) gating, PDPL (Law 151/2020)
> consent, and bilingual health-information disclaimers are built in. See
> [`legal/RXEG-LEGAL-001.md`](legal/RXEG-LEGAL-001.md). Do not ship without the
> blocking controls listed there.

## Stack

- **Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 · PostgreSQL 15 · JWT
- **Frontend:** Vanilla HTML/CSS/JS (no build step — fast load on mobile, AR/EN RTL)
- **Payments:** Paymob (hooks built; needs live credentials)
- **Hosting target:** Fly.io · CDN: Cloudflare

## Layout

```
rxegypt-pilot/
├── backend/          FastAPI app, models, routes, drug seed DB
├── frontend/         Patient app, pharmacy POS, Dawai patient app, API client
├── legal/            Compliance framework + grant strategy
└── docs/             API specification
```

## Quick start — backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then edit values

# Seed the drug DB (creates tables + 30 sample Egyptian drugs)
python seed/seed_drugs.py

uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs
```

## Quick start — frontend

```bash
cd frontend
python -m http.server 3000
# open http://localhost:3000/index.html
```

The frontend runs in **demo mode** (bundled sample data, no backend) until you
point it at the API. To use the live backend, set before loading any page:

```js
window.RXEGYPT_API_URL = 'http://localhost:8000/api/v1';
```

## Key features

- **Drug search** (EN/AR/generic) + **EAN-13 barcode lookup**
- **Rx gating:** orders with prescription-only drugs go to
  `pending_rx_verification` and require pharmacist confirmation (WhatsApp flow)
- **PDPL consent modal** — bilingual, logged with timestamp before data processing
- **Health Information Guide** — general info only, bilingual disclaimers, no
  diagnosis / severity / Rx suggestions
- **Pharmacy POS** — barcode sale entry + stock updates
- **Inventory** — low-stock report, pharmacist-only writes

## Deploy (Fly.io)

```bash
fly launch --name rxegypt-pilot
fly secrets set DATABASE_URL="..." SECRET_KEY="..." PAYMOB_API_KEY="..."
fly deploy
```

---
🌿 ✦ ASTRA INTELLIGENCE SERVICES ✦ 🌿 | ⚜ MISR ⚜
RxEgypt Pilot · README · Experts Pharmacy Hurghada
