# Phase 4 — Project Lineage Analysis

## Related group 1: the AISE portfolio pair (Luxor + RxEgypt)

The two confirmed applications are **siblings, not forks**. They share no
domain code but were deliberately converged on shared conventions:

| Shared trait | Evidence |
|---|---|
| Single Git history | Both live in `fly-ai-guy7/expert-spork` (54 commits); RxEgypt merged in as a subtree of the same repo |
| Design-token contract | `DESIGN_SYSTEM.md` (2026-06-24): identical semantic token names (`--ink/--muted/--line/--sand/--accent/--accent-d/--radius/--shadow`) implemented in `frontend/src/styles.css` and `rxegypt-pilot/frontend/theme.css`; commit `3b6da5d` "Unify AISE design-token contract across Luxor + RxEgypt" |
| FastAPI backend idiom | Both: FastAPI + uvicorn, `/healthz`-style probes, env-driven CORS, `.env.example` templates, pinned `requirements.txt` |
| WhatsApp as the primary business channel | Luxor: booking/concierge deep links (`App.jsx` `WA` const); RxEgypt: pharmacist Rx-verification line (`PHARMACIST_WHATSAPP`) |
| Deployment pattern | Dockerfile per tier + platform config (render.yaml+vercel.json vs fly.toml+compose) + path-scoped GitHub Actions CI per app |
| Documentation pattern | README + status/plan docs; RxEgypt adds CLAUDE.md + legal/provenance docs |
| Market | Both Egypt-focused (Luxor West Bank; Hurghada/Red Sea), EGP/GBP pricing, AR relevance |

**Probable original:** Luxor Guest House (root position, `version 1.0.0`,
simpler stack). **Most advanced:** RxEgypt (auth, DB, migrations, 70 tests,
audit trail). **Best-designed UI:** Luxor. **Best-tested:** RxEgypt.

There is no migration between them to plan — each is canonical in its own
family. The shared artefact to preserve and formalise is the **token
contract**, plus the conventions listed above.

## Possible external relatives (unverifiable this session)

1. **Luxor Guest House ↔ "Luxor Smart Trip Planner"** — name overlap and the
   tours/concierge feature set suggest possible shared lineage on the Mac.
   Before choosing the travel-template donor, diff the two locally (routes,
   `package.json`, git remotes).
2. **rxegypt-pilot ↔ a standalone "RXEGYPT" repo** — the brief lists RXEGYPT
   as a separate known project. If a standalone clone exists on the Mac, this
   in-repo pilot (last touched 2026-06-24, CI-covered) is likely the more
   advanced line; verify by comparing Alembic revision heads and test counts
   before declaring canonical.
3. **Atlas Voyage / Voyara / Astra Travel Egypt / Destination Factory** — the
   brief implies a family of travel builds. None are present here. The
   duplication analysis for that group can only be done on the Mac; use the
   comparison checklist in `DUPLICATION_REPORT.md`.

## Files/modules worth preserving regardless of future consolidation

- `DESIGN_SYSTEM.md` + both `:root` token blocks (the contract itself)
- `rxegypt-pilot/backend/security.py` (JWT + role guards), `audit.py`,
  consent/data-subject-rights routes, `config.py` prod-guard pattern
- `rxegypt-pilot/backend/seed/build_egyptian_drugs.py` + `PROVENANCE.md`
  (reproducible, integrity-checked data pipeline — a model for content import
  tooling)
- Luxor `backend/app/main.py` ledger pattern + atomic JSON writes
- Luxor `scripts/smoke_api.sh` (post-deploy smoke test pattern)
- Both CI workflows (path-scoped multi-app CI in one repo)

**Nothing was archived, and no repository was declared safe to archive** —
that judgement needs the Mac-side inventory first.
