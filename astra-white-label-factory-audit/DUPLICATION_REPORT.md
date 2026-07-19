# Duplication Report

## Duplication found inside the audited repository

Low overall — the repo is disciplined. Items found:

| # | Duplication | Locations | Assessment |
|---|---|---|---|
| 1 | Design-token `:root` blocks (intentional twin implementations of one contract) | `frontend/src/styles.css` · `rxegypt-pilot/frontend/theme.css` | **By design** (different stacks/deploys, per `DESIGN_SYSTEM.md`). Becomes real duplication the moment a third product copies it — that is the trigger to create `packages/design-tokens`. |
| 2 | FastAPI app scaffolding (CORS setup, env parsing, health endpoint idiom) | `backend/app/main.py` · `rxegypt-pilot/backend/main.py`+`config.py` | Convergent pattern, ~30 lines each. Candidate for a small shared backend starter in the factory, not urgent. |
| 3 | `.env.example` + Dockerfile-per-tier + path-scoped CI conventions | both apps | Healthy convention reuse; formalise as template scaffolding. |
| 4 | WhatsApp deep-link construction | `App.jsx` (`https://wa.me/…`), ledger `contacts.json`, RxEgypt WhatsApp flow | Same integration written twice; belongs in `packages/integrations` (whatsapp adapter) later. |
| 5 | Brand/contact facts duplicated *within* Luxor | WhatsApp number appears hard-coded in `App.jsx` (`WA` const) **and** in `backend/app/ledger/contacts.json`; address string duplicated in `Footer` fallback and README | Real defect for white-labelling: two sources of truth. Fix during template extraction (frontend should consume `/api/contacts` only). |
| 6 | Rating "9.0 / 470 reviews" duplicated | `contacts.json` + fallback literals in `Hero` (`"9.0"`) + README prose | Same issue as #5. |

## Checklist for the Mac-side duplication pass (travel family)

When Atlas Voyage / Voyara / Astra Travel Egypt / Luxor Smart Trip Planner /
Destination Factory are located, compare per pair:

1. `git log --reverse --format='%H %ci %s' | head -5` — shared root commits?
2. `package.json` name/deps diff; lockfile similarity
3. Route/page inventory diff; component filename overlap
4. Asset hashes (`shasum` on images/logos)
5. Env-var name overlap in `.env.example`
6. Copied copy: grep distinctive strings ("Valley of the Kings", brand lines)
7. Schema/content-model overlap (rooms/tours/itineraries)

Record results by extending `project-registry.json` (each project entry gains
`lineageGroup` and `recommendedCanonical` fields).
