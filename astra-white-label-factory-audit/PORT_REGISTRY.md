# Port Registry

Machine-readable version: `port-registry.json`.
Ports observed listening in the audited container: **none** (harness only).
Everything below is *documented/expected* usage from repository evidence, plus
the Mac-side claims from the brief (unverified).

## Confirmed by repository evidence

| Port | Service | Source of truth | Conflict? |
|---|---|---|---|
| 8000 | Luxor Guest House API (uvicorn) | root `README.md` run instructions | **YES — collides with RxEgypt API** |
| 8000 | RxEgypt API (uvicorn / compose) | `rxegypt-pilot/README.md`, `docker-compose.yml` | **YES — same default as Luxor** |
| 5173 | Luxor frontend (Vite dev) | Vite default; CORS list in `backend/app/main.py` | no |
| 4173 | Luxor frontend (Vite preview) | Vite default for `npm run preview` | latent — same default as Atlas Voyage on the Mac |
| 3000 | RxEgypt frontend (static server) | `rxegypt-pilot/README.md`; backend CORS default | latent — Mac's "unidentified :3000" may be this or another dev server |
| 8080 | Luxor frontend container (nginx) | `PROJECT_STATUS.md` container row | **latent — Dashy uses 8080 on the Mac** |

## Mac-side claims (not verifiable from this session)

| Port | Claim | Status |
|---|---|---|
| 8080 | Dashy (Bruce OS dashboard) | unverified |
| 4173 | Atlas Voyage `#workflow` | unverified |
| 3000 | Unidentified web application | unverified — identify with `lsof -iTCP:3000 -sTCP:LISTEN` |
| 8000 | Historic multi-backend reuse | **consistent with in-repo evidence** — both audited backends default here |

## Proposed permanent assignments (factory registry seed)

Once the factory's `registry/ports.json` exists, assign stable dev ports per
project so collisions stop being folklore:

| Range | Purpose | Initial assignments |
|---|---|---|
| 8000–8099 | Backend APIs | 8000 → *retire as a shared default*; 8001 luxor-guest-house API; 8002 rxegypt API |
| 3000–3099 | Frontend dev servers (non-Vite) | 3002 rxegypt web |
| 5173+/4173+ | Vite dev/preview | 5173/4173 luxor web (until another Vite app needs them) |
| 8080 | **Reserved for Dashy** — never assign to app containers locally | remap Luxor nginx to 8081 for local runs |

These are proposals only; nothing was changed this phase. Adopting them
requires a one-line change per project (`--port` flag / compose mapping) in a
later authorised phase.
