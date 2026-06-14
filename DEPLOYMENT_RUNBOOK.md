# Deployment Runbook — Luxor Guest House

This runbook deploys the **backend to Render** and the **frontend to Vercel**.
Deploy the backend first so you have its URL ready for the frontend.

- Backend (FastAPI) → **Render**
- Frontend (React + Vite) → **Vercel**

Estimated time: ~15–20 minutes.

---

## 0. Prerequisites

- The repository is pushed to GitHub.
- Accounts on [Render](https://render.com) and [Vercel](https://vercel.com),
  each connected to your GitHub account.
- (Optional) A custom domain.

---

## 1. Deploy the backend to Render

You can use the **Blueprint** (`render.yaml`, recommended) or configure the
service manually.

### Option A — Blueprint (recommended)

1. In Render, click **New → Blueprint**.
2. Select this repository. Render reads `render.yaml` and proposes a web
   service named **luxor-guest-house-api**.
3. Confirm the settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Click **Apply** and wait for the first deploy to finish.
5. Copy the service URL, e.g. `https://luxor-guest-house-api.onrender.com`.
6. Verify: open `https://<your-api>.onrender.com/` and `…/docs`.

### Option B — Manual web service

1. **New → Web Service**, pick the repo.
2. Set:
   - **Runtime:** Python 3
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Create the service and wait for it to go live.

### Backend environment variables (Render → Settings → Environment)

| Key               | Value                                                            |
| ----------------- | --------------------------------------------------------------- |
| `ALLOWED_ORIGINS` | Your Vercel frontend URL once known, e.g. `https://luxor-guest-house.vercel.app` (comma-separate multiple). |
| `PYTHON_VERSION`  | `3.12.4` (already set by the blueprint).                        |

> `*.vercel.app` domains are already permitted by the backend CORS regex, so
> `ALLOWED_ORIGINS` is mainly needed for a **custom** production domain.

> **Persistence note:** On Render's free plan the filesystem is ephemeral, so
> booking enquiries in `database/bookings.json` reset on each redeploy/restart.
> For durable storage, attach a persistent disk (see the commented block in
> `render.yaml`) and set `BOOKINGS_FILE=/var/data/bookings.json`, or move to a
> managed database.

---

## 2. Deploy the frontend to Vercel

1. In Vercel, click **Add New… → Project** and import this repository.
2. Configure the project:
   - **Root Directory:** `frontend`  ← important, the app lives in a subfolder
   - **Framework Preset:** Vite (auto-detected)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Add an **Environment Variable**:

   | Key            | Value                                            |
   | -------------- | ------------------------------------------------ |
   | `VITE_API_URL` | Your Render backend URL (no trailing slash), e.g. `https://luxor-guest-house-api.onrender.com` |

4. Click **Deploy**. Vercel builds and gives you a URL, e.g.
   `https://luxor-guest-house.vercel.app`.

---

## 3. Connect the two

1. Copy the Vercel frontend URL.
2. In Render, set `ALLOWED_ORIGINS` to that URL (only needed for non-`vercel.app`
   custom domains) and trigger a redeploy if you changed it.
3. Reload the frontend — rooms, tours, the concierge and the booking form should
   all load live data from the backend.

---

## 4. Smoke test (post-deploy)

Run these against your live API (replace the host):

```bash
API=https://luxor-guest-house-api.onrender.com

curl -s $API/                       # service info
curl -s $API/api/rooms              # 5 rooms
curl -s $API/api/tours              # 19 tours
curl -s $API/api/dashboard          # KPIs

# Concierge
curl -s -X POST $API/api/concierge \
  -H "Content-Type: application/json" \
  -d '{"message":"Which rooms have a river view?"}'

# Create a booking enquiry
curl -s -X POST $API/api/bookings \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Guest","email":"test@example.com","guests":2}'
```

In the browser:

1. Open the Vercel URL — confirm rooms, tours and the concierge load.
2. Submit the **Booking Enquiry** form → expect a success message with a ref.
3. Open the **Dashboard** tab → the new enquiry and KPIs appear.
4. Confirm the **WhatsApp** buttons open `https://wa.me/201001842081`.

---

## 5. Rollback

- **Render:** Deploys tab → pick a previous successful deploy → **Rollback**.
- **Vercel:** Deployments tab → previous deployment → **Promote to Production**.

---

## 6. Go-live checklist

- [ ] Backend healthy at `/` and `/docs`.
- [ ] Frontend loads live rooms, tours and concierge replies.
- [ ] Booking enquiry submits and appears on the dashboard.
- [ ] `VITE_API_URL` points at the production backend.
- [ ] `ALLOWED_ORIGINS` includes any custom production domain.
- [ ] Replace placeholder email `info@luxorguesthouse.local` with a real mailbox.
- [ ] Decide on durable storage for bookings (disk or database) before relying
      on enquiries persisting.
- [ ] Review `backend/app/ledger/assumptions.json` and confirm/replace each item.
