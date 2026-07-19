# Phase 7 — Factory Architecture Proposal

## Verdict on the proposed structure

The suggested `~/bruce-os/astra-white-label-factory/` layout (apps/, packages/,
templates/, clients/, tooling/, registry/, docs/, qa/) is **directionally
right and is adopted** — with three evidence-based amendments:

### Amendment 1 — Start with 4 packages, not 14

Only two products exist in scope, on **different frontend stacks** (React+Vite
vs no-build HTML). Thirteen of the fourteen suggested packages would be
speculative. Evidence-backed starters:

| Package | Seeded from | Why now |
|---|---|---|
| `packages/design-tokens` | `DESIGN_SYSTEM.md` + both `:root` blocks | Already a proven two-brand contract; add a validator so drift becomes a CI failure |
| `packages/config` | RxEgypt `config.py` prod-guard + `docker-entrypoint.sh` runtime injection + the client schema (see `CLIENT_CONFIG_SCHEMA_PROPOSAL.md`) | The heart of "configuration-driven client instance" |
| `packages/auth` | RxEgypt `security.py` + auth routes (JWT, roles, consent, data-subject rights, audit hooks) | Highest-quality, most portable backend capability in scope |
| `packages/integrations` | WhatsApp (both apps) + Paymob (`payments.py`, mock-first) | The two integrations real clients already need |

`ui`, `forms`, `i18n`, `motion`, `analytics`, `seo`, `permissions` (folded
into auth for now), `content-schema` (starts as JSON-Schema files inside
`packages/config`), `testing`, `notifications` — **create each one the day a
second consumer exists**, per decision principle 12 (fewest moving parts).

### Amendment 2 — Templates follow evidence, not the full taxonomy

Create `templates/` entries only when a donor or a paying need exists:

- `templates/guesthouse` — from Luxor (pilot 1). Covers travel + small-hotel.
- `templates/pharmacy` — from RxEgypt (pilot 3).
- `templates/restaurant` — pending Marina Ember inspection (pilot 2).
- travel/hotel/compliance/health/legal/compound as distinct templates: **defer**
  until their donor projects are located and assessed on the Mac.

### Amendment 3 — The factory monorepo does NOT absorb existing repos

`expert-spork` keeps running as-is until each pilot's migration is proven
(decision principle 2). The factory starts as a *new* workspace that imports
extracted code; existing apps are retired only after their client instance
passes the QA gate in production.

## Proposed structure

```
~/bruce-os/astra-white-label-factory/
├── apps/                  # long-lived internal apps (e.g. factory console) — empty at first
├── packages/
│   ├── design-tokens/     # contract + per-brand token sets + drift validator
│   ├── config/            # client schema (JSON Schema), loader, validate-config lib
│   ├── auth/              # JWT/roles/consent/audit (Python lib first; TS later if needed)
│   └── integrations/      # whatsapp/, paymob/ adapters (mock-first)
├── templates/
│   └── guesthouse/        # pilot 1: extracted from Luxor
├── clients/
│   └── luxor-guest-house/ # client instance #1: config + content + branding ONLY (no code)
├── tooling/
│   ├── create-client/     # scaffold a client dir from a template + schema
│   ├── validate-config/   # schema + secrets-absence + port-registry checks
│   ├── production-qa/     # the QA pipeline (see QA_AUTOMATION_PLAN.md)
│   └── register-project/  # updates registry/*.json (Dashy sync deferred — Dashy is read-only this phase)
├── registry/
│   ├── projects.json      # seeded from this audit's project-registry.json
│   ├── ports.json         # seeded from port-registry.json
│   ├── templates.json
│   ├── clients.json
│   └── deployments.json
├── docs/                  # this audit moves/links here
└── qa/                    # QA reports, screenshots, visual baselines per client
```

`registry/components.json` and the remaining tooling
(`discover-local`, `migrate-project`, `import-content`, `visual-qa`,
`release-client`, `update-dashy`) are **planned second-wave** — each has a
clear seed (e.g. `import-content` from RxEgypt's provenance-verified seed
pipeline; `production-qa`'s smoke stage from `scripts/smoke_api.sh`) but no
consumer until pilot 1 runs.

## The factory equation, mapped to evidence

```
tested product template      → templates/guesthouse   (from Luxor, CI-tested)
+ client configuration       → clients/<id>/client.json (schema proposed)
+ content                    → clients/<id>/content/*.json (ledger pattern, proven)
+ branding                   → clients/<id>/brand/ tokens + assets (token contract, proven)
+ integrations               → packages/integrations adapters (whatsapp/paymob, proven or wired)
= deployable client instance → Docker image + platform config (Dockerfiles/render/fly patterns, proven)
```

Every right-hand element already exists in embryo in this repository — the
factory is a formalisation, not an invention. **A new client is a new
`clients/<id>/` directory, never a new codebase** (decision principle 7).

## Technology guardrails

- **Workspace:** pnpm workspace + turbo *only when* JS packages ≥2; Python
  side uses plain per-package `pyproject.toml` — no premature build system.
- **Compatibility:** Docker + GitHub Actions + Render/Vercel/Fly (all already
  in use); no new paid services introduced (principle 14).
- **Operable locally by Bruce:** every tooling command must run as a single
  documented shell command on the Mac (principle 13); no k8s, no bespoke infra.
- **Mixed stacks accepted:** the factory serves a React template and a
  static-HTML template side by side; shared packages are contracts (tokens,
  schemas) before they are code, which is exactly how `DESIGN_SYSTEM.md`
  already works.
