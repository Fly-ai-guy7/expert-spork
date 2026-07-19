# Recommended Migration Sequence

Ordered so that every step is reversible, existing apps keep running
(decision principle 2), and each phase's output is the next phase's input.
**Nothing below is started until Bruce/Emma approve this audit.**

## Step 0 — Complete discovery on the Mac (prerequisite, ~half a day)
Run this same audit brief in a Claude Code session on the Mac: full project
inventory, localhost/process audit (identify :3000, confirm Dashy :8080 and
Atlas Voyage :4173), locate Atlas Voyage/Voyara/Marina Ember and the rest of
the 23 unobserved projects, and extend `project-registry.json` in place.
**Everything after this step may be re-ordered by what the Mac reveals.**

## Step 1 — Decisions gate (Bruce + Emma)
Confirm: travel-template donor (Luxor vs Atlas Voyage), pilot order, port
assignments, factory location `~/bruce-os/astra-white-label-factory/`.

## Step 2 — Factory skeleton + registries (low risk, ~1 day)
Create the workspace (per `FACTORY_ARCHITECTURE_PROPOSAL.md`), seed
`registry/*.json` from this audit, add `tooling/validate-config` with the
client schema. No existing repo is touched.

## Step 3 — `packages/design-tokens` (~1 day)
Formalise the AISE contract + brand token sets + drift validator. Existing
apps keep their local copies until each pilot migrates (no forced upgrade).

## Step 4 — Pilot 1: travel template + Luxor client instance (~1–2 weeks)
Extract `templates/guesthouse` from Luxor per `PILOT_TEMPLATE_ASSESSMENT.md`:
fix L1/L2 security items, de-hard-code per `WHITE_LABEL_READINESS.md`, build
`clients/luxor-guest-house/` (config+content+brand only), stand up QA wave 1,
deploy to preview, compare against the original app. **Original Luxor app
stays untouched and running until the instance passes QA in production.**

## Step 5 — Validate the factory with client #2 (~2–3 days)
Create a fictional second travel client (different brand/content/language
set) purely from configuration. This is the proof of the factory equation —
if it needs code changes, the template isn't done. Include an AR/RTL variant
to force the i18n path early.

## Step 6 — Pilot 2: restaurant template (~1–2 weeks)
Marina Ember as donor if Step 0 validates it; otherwise derive from the
travel template (menus ≈ rooms ledger swap). Same QA gate.

## Step 7 — Shared backend capabilities (`packages/auth`, `integrations`) (~1 week)
Extract RxEgypt's auth/consent/audit + WhatsApp/Paymob adapters once two
templates want them (rule: no package without a second consumer).

## Step 8 — Pilot 3: pharmacy template (after RxEgypt go-live blockers clear)
Only after EDA reconciliation (R1), Paymob validation (R2) and the PSA (R3).
The live pilot client must never be destabilised by templating work.

## Step 9 — Registry-driven operations
`/release-client`, `registry/deployments.json`, and (with explicit
authorisation) the Dashy sync tooling. Archiving of superseded repos happens
only here, with per-repo approval.

## Risk controls throughout
- Existing repos are read-only donors until their replacement passes QA.
- No force pushes, no history rewrites, no bulk moves (standing rules).
- Every step ends with registries updated + a `/handoff` status pack.
