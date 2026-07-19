# QA Automation Plan

The gate every generated client instance must pass before release.
Principle (from the brief, endorsed by evidence): **a successful compile is
not evidence of completion** — Luxor's own docs already model this
(`TESTING.md` + CI + smoke script beyond the build).

## Pipeline stages (`tooling/production-qa`)

| # | Stage | Tooling | Exists today? |
|---|---|---|---|
| 1 | Clean-environment install | fresh container/venv; `npm ci` / `pip install -r` | ✅ CI does this (both apps) |
| 2 | Production build | `npm run build` / docker build | ✅ CI (Luxor build job) |
| 3 | Lint | ruff (py) — **add ESLint for JS templates** | ◐ RxEgypt only |
| 4 | Type check | **add**: mypy or pyright (py), TS/JSDoc check (js) | ✗ |
| 5 | Unit tests | pytest / node test | ✅ 11 + 70 tests exist |
| 6 | Integration tests | pytest against migrated DB + seeded content | ✅ RxEgypt CI pattern |
| 7 | Playwright E2E | core funnels per template (booking enquiry; POS sale; consent flow) | ✗ — Chromium pre-installed in remote env, build on it |
| 8 | Console-error check | Playwright listener fails run on console errors | ✗ |
| 9 | Broken-link check | crawler over built site | ✗ |
| 10 | Screenshots | desktop 1440 / tablet 768 / mobile 390, per key page | ✗ |
| 11 | Visual regression | screenshot diff vs `qa/baselines/<client>/` | ✗ |
| 12 | Locale layouts | run 7–11 per enabled language; **Arabic RTL run required** whenever `languages.rtl` non-empty | ◐ RxEgypt has RTL to test against |
| 13 | Keyboard navigation | Playwright tab-order assertions on forms/modals | ✗ |
| 14 | Accessibility | axe-core scan; fail on serious/critical; contrast check feeds from token validator | ✗ |
| 15 | Reduced motion | run key pages with `prefers-reduced-motion`; assert no essential info lost | ✗ (no motion yet — cheap to mandate now) |
| 16 | Performance | Lighthouse budget per template (start: perf ≥ 80 mobile) | ✗ |
| 17 | Security review | secret-scan diff, dependency audit (`npm audit`/`pip-audit`), auth-required-endpoint probe, prod-guard boot test (RxEgypt pattern) | ◐ patterns exist |
| 18 | Env-var validation | `validate-config` + boot-with-missing-var matrix | ◐ `config.py` guard is the seed |
| 19 | Deployment health check | deploy to preview → `smoke_api.sh`-style probe of `/healthz` + key endpoints | ✅ seed: `scripts/smoke_api.sh` |

Output: `qa/reports/<clientId>/<timestamp>/` containing JSON verdict,
markdown summary, screenshots, diffs — the artefact set steps 10 ("produce
screenshots and reports") and 11 ("approve") of the production process
consume.

## Rollout order

1. **Wave 1 (pilot 1 gate):** stages 1–7, 10, 17–19 — largest risk coverage
   per effort, and every stage has an existing seed or a pre-installed tool.
2. **Wave 2:** 8, 9, 12, 14 (console, links, locales, axe).
3. **Wave 3:** 11, 13, 15, 16 (visual regression once designs stabilise;
   budgets once baseline numbers exist).

## Standing rules

- QA runs in a clean environment, never the dev working tree.
- A red stage blocks release; overrides require Bruce's explicit approval
  recorded in the QA report.
- Baselines are per-client (brand differences are not regressions).
- The QA runner never has production secrets; preview deploys use scoped
  keys.
