# Pilot Template Assessment

The brief proposed: **(1) Atlas Voyage or Voyara** for the travel template,
**(2) Marina Ember** for the restaurant template.

## 1. Travel template — Atlas Voyage / Voyara

| Question | Finding |
|---|---|
| Can it be located? | **No.** Neither exists in the audited environment. Atlas Voyage is claimed at `localhost:4173/#workflow` on the Mac; not reachable from this session. |
| Functional? | Unknown. |
| Strongest available foundation? | **Cannot be confirmed.** The strongest travel foundation *actually observable* is `luxor-guest-house`. |

**Evidence-based challenge to the assumption:** the audit cannot endorse
Atlas Voyage as pilot #1 while it is unverified. Two scenarios for the Mac
follow-up:

- *Scenario A — Atlas Voyage is real, functional, and already
  workflow/white-label oriented:* it likely becomes the travel template donor,
  and Luxor becomes its **first client instance** (a real property with real
  content — an ideal validation client) plus the donor of the enquiry/concierge
  workflows and the token contract.
- *Scenario B — Atlas Voyage is a design prototype or unstable:* extract the
  travel template from Luxor (assessment below) and lift Atlas Voyage's best
  screens/flows as designs, not code.

Either way the **client-config schema and token contract work is identical**,
so that work is not blocked on locating Atlas Voyage.

### Luxor Guest House as the fallback travel-template donor

- **Functional:** yes — builds green, 11 backend tests pass in CI, smoke
  script, deployment runbook (~85% deploy-ready per `PROJECT_STATUS.md`).
- **Extract into template:** app shell, booking-enquiry workflow, concierge
  engine, ledger content pattern, dashboard, token-driven styling, photo-slot
  system, Docker/CI/deploy scaffolding.
- **Stay product-specific:** guest-house domain copy, tours module semantics.
- **Become configurable:** everything in `WHITE_LABEL_READINESS.md` (brand
  constants, reviews, experiences, currency, concierge vocabulary, ports).
- **Rewrite:** fake `Calendar()` (remove or make real); the hard-coded
  fallback literals; GBP-specific KPI field name.
- **Test additions:** frontend component tests (none exist), Playwright E2E
  for the booking funnel, a11y baseline.
- **Security before templating:** auth on `/api/bookings` + `/api/dashboard`;
  rate limiting on POST endpoints (both already documented in
  `SECURITY_NOTES.md`).
- **Migration complexity: LOW-MEDIUM** (~2–4 days to configurable template +
  ~1–2 days security/testing).

## 2. Restaurant template — Marina Ember

| Question | Finding |
|---|---|
| Can it be located? | **No.** Not in the audited environment; Mac-side only. |
| Functional? | Unknown. |

**Assessment deferred** — but note the structural overlap: a restaurant
platform's core loop (menu browsing → enquiry/reservation → WhatsApp →
staff dashboard) is ~70% the Luxor loop with "rooms/tours" swapped for
"menus/tables". If Marina Ember turns out weak, the restaurant template can be
derived from the travel template's foundation rather than built from scratch.
The Luxor ledger pattern (`rooms.json` → `menus.json`) transfers directly.

## Unsolicited but evidence-backed: RxEgypt as a pilot

RxEgypt is the best-engineered project in scope, but it is a **poor first
white-label pilot**: regulated domain, unsigned liability agreement, EDA
reconciliation outstanding, and a client-specific legal surface. Use it as the
**capability donor** (auth, audit, consent, payments, config injection) and
white-label it later as `templates/pharmacy` once the factory pattern is
proven on lower-risk domains.

## Recommended pilot order

1. **Pilot 1 — Travel:** Luxor Guest House → `templates/guesthouse`
   (renameable to `templates/travel` later), with Luxor itself as client
   instance #1. If the Mac audit upgrades Atlas Voyage to donor, Luxor becomes
   client #1 of *that* template instead — either way this starts now.
2. **Pilot 2 — Restaurant:** Marina Ember *if it survives inspection on the
   Mac*; otherwise derive from the travel template.
3. **Pilot 3 — Pharmacy/compliance:** RxEgypt, after go-live blockers clear.
