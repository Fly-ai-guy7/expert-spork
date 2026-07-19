# Phase 6 — White-Label Readiness Analysis

## Luxor Guest House (readiness 5/10)

The split is unusually clean for an MVP: **content is already externalised**
(JSON ledger served over the API), but the **frontend re-hard-codes brand
facts** on top of it.

### Hard-coded inventory (file:evidence)

| Item | Where | Should move to |
|---|---|---|
| Brand name "Luxor / GUEST HOUSE" | `App.jsx` `Header`/`Footer`, `index.html` title | client config (branding) |
| WhatsApp number `+201001842081` | `App.jsx` `WA` const (duplicates ledger `contacts.json`) | client config → consumed via `/api/contacts` only |
| Address, email, rating, review count | `contacts.json` (good) **and** fallback literals in `Hero`/`Footer` | keep in content records; delete JSX fallbacks or make them config-fed |
| Guest reviews (3 fake-ish testimonials) | `App.jsx` `REVIEWS` | content files / CMS records |
| Experiences list + map pins | `App.jsx` `EXPERIENCES`, `MAP_PINS` | content files |
| Marketing copy (hero text, why-stay features, concierge suggestions) | `App.jsx` throughout | content files |
| Currency `£` and "GBP" KPI label | `roomPrice()`, dashboard KPI key `avg_room_reference_price_gbp` | client config (currency) + neutral API field name |
| Colour palette / fonts (gold, Playfair) | `styles.css` `:root` | design tokens per client — mechanism already exists via `--accent` aliasing |
| Photo placeholders `.ph-*` → SVGs | `styles.css` + `public/img/` | branding assets (documented drop-in slots already exist) |
| Concierge keyword sets (rooms/tours/policy/contact terms, "ahmed", "luxor", "nile") | `backend/app/main.py` keyword sets | template config (domain vocab) + client content |
| Deployment names (`luxor-guest-house-api` etc.) | `render.yaml`, `vercel.json`, README examples | deployment config per client |
| Rooms, tours, policies, FAQ, contacts | `backend/app/ledger/*.json` | **already correct** — becomes the content-schema exemplar |

**Conversion estimate: SMALL-to-MEDIUM — roughly 2–4 focused days.**
1. Frontend: replace ~8 hard-coded constants/blocks with data from
   `/api/contacts` + a new `/api/content` (or build-time config import); 
2. tokens: split brand values from semantic tokens (mechanism exists);
3. backend: rename GBP-specific field, load ledger dir from env
   (`LEDGER_DIR`), parameterise concierge vocab;
4. delete or wire the fake calendar; add auth to staff endpoints (security
   prerequisite, ~1 day extra).

## RxEgypt Pilot (readiness 5/10)

Backend is largely config-driven already (`config.py`: app name, WhatsApp
line, CORS, payments all env-driven; `docker-entrypoint.sh` injects the
frontend API URL at runtime). The pilot-client identity is baked into the
HTML suite.

### Hard-coded inventory

| Item | Where | Should move to |
|---|---|---|
| "Experts Pharmacy" branding + Hurghada identity | `frontend/index.html` (patient app is "Experts Pharmacy branded" per CLAUDE.md), page titles/copy | client config (branding) |
| Suite navigation labels/links | `nav.js` | client config |
| Pharmacy green palette | `theme.css` brand tokens | design tokens per client (contract already in place) |
| Bilingual strings (AR/EN) | inline in `dawai-patient.html` etc. | `packages/i18n` string tables |
| Demo-mode sample data | `rxegypt-api.js` | template fixture files |
| App name default "RxEgypt Pilot — Experts Pharmacy Hurghada" | `config.py` default | env already overrides; change default to neutral |
| Seed example email domain `experts.eg` | README/CLAUDE.md examples only | docs cleanup |
| Egyptian drug catalogue + Rx heuristics | `seed/` | **correct as a market-level (not client-level) content pack** — Egypt-market clients share it |
| Legal texts (PDPL consent wording, disclaimers) | inline in pages | content files with legal review per client |

**Conversion estimate: MEDIUM — roughly 1–2 weeks**, because the frontend is
four hand-written HTML pages (no componentisation to lean on) and the legal
wording must be treated as reviewed content, not just strings. The backend
needs comparatively little (multi-tenant questions deferred — a pilot per
pharmacy via config/deploy-per-client is the low-risk path, consistent with
decision principle 7).

## Target destinations summary

| Destination | Gets |
|---|---|
| Client configuration | identity, brand names, contact channels, currency, locales, feature flags, deployment names |
| Environment configuration | API URLs, CORS, secrets *(names only — values in host secrets)* |
| Content files | rooms/tours/menus/FAQ/policies/reviews/experiences/map pins/marketing copy |
| CMS/database records | anything the client edits after launch (defer CMS choice; JSON ledger works for pilot #1) |
| Feature flags | concierge on/off, dashboard, payments mock/live, health-guide module |
| Design tokens | palette, fonts, radius, shadows (mechanism proven) |
| Integration adapters | WhatsApp, Paymob, future email/analytics |
