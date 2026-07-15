# Security Review — Phase 1 Audit

**Scope:** `Fly-ai-guy7/expert-spork` working tree + Claude Code configuration surface, 2026-07-15. Static review only (audit phase — nothing executed against live services, nothing installed).

## 1. Secrets

| Check | Result |
|---|---|
| Tracked `.env`/key/token files | ✅ None — only `.env.example` files with blank/placeholder values |
| Hardcoded credentials grep (py/js/json/yml/toml/html) | ✅ Only test fixtures asserting the dev-key boot guard (`rxegypt-pilot/backend/tests/test_config.py`) |
| `.gitignore` coverage | ✅ `.env`, `*.env` excluded, `!.env.example` allowed |
| Git history spot-check | Recent history clean; **recommend** a one-time `run_secret_scanning` / gitleaks pass over full history in Phase 6 CI |
| Claude config secrets | ✅ None — no user/project settings contain credentials; MCP auth is account-level |

## 2. Dependency findings

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| D1 | `python-jose==3.3.0` (RxEgypt JWT) — effectively unmaintained, historical CVEs (e.g. algorithm-confusion class) | **High** | Replace with `PyJWT` or `joserfc`; small surface (`security.py`), straightforward swap. Do in Phase 6/7, not during audit |
| D2 | `vite@^5.3.1` — old line; known dev-server CVEs (dev-only exposure, e.g. arbitrary file read via crafted requests to the dev server) | Medium (dev-only) | Bump to current Vite 5.x/6.x on next frontend touch; never expose `npm run dev` publicly |
| D3 | FastAPI 0.110/0.111, SQLAlchemy 2.0.29, Alembic 1.13.1 — behind current but no known critical CVEs in this usage | Low | Routine bump cadence; add `pip-audit` + `npm audit` + Dependabot in Phase 6 |
| D4 | `bcrypt==4.1.2`, `pydantic` 2.x pins | OK | Fine |
| D5 | No lockfile-integrity or dependency scanning in CI | Medium | Phase 6: Dependabot config + `pip-audit`/`npm audit --audit-level=high` CI steps |

## 3. Application-level observations (existing products)

| # | Finding | Severity | Notes |
|---|---|---|---|
| A1 | Luxor backend CORS allows any `*.vercel.app` origin | Medium | Fine for demo; tighten to the exact production origin before real bookings (tracked in SECURITY_NOTES.md) |
| A2 | Luxor `GET /api/bookings` and `/api/dashboard` are unauthenticated | Medium | Guest PII (names/contacts in enquiries) readable by anyone with the API URL. Acceptable for prototype; add staff auth before go-live — flagged as an unauthenticated-administrative-route class issue |
| A3 | RxEgypt: prod boot guard refuses weak SECRET_KEY | ✅ Good | Keep |
| A4 | RxEgypt: server-side Rx gating, controlled-substance blocking, PDPL consent enforcement, audit trail | ✅ Good | These are release-blocking invariants — encode as "prohibited changes" in root CLAUDE.md |
| A5 | Paymob HMAC callback wired but untested against live credentials | Medium | Validate before payment go-live (already in rxegypt CLAUDE.md priorities) |
| A6 | Booking/PII stored in flat JSON on ephemeral disk (Luxor) | Low/Medium | Durability + data-protection concern; move to managed DB before real traffic |

## 4. Operating-layer security requirements (feed into Phases 4–6)

1. **Hooks** (see hook-registry.md): secret-write blocking, destructive-command gate, dirty-tree deploy block, force-push prevention.
2. **CI** (Phase 6): pinned `anthropics/claude-code-security-review` on PRs — ⚠ upstream explicitly notes it is **not hardened against prompt injection**; require maintainer approval before workflows run on external-contributor PRs. `ANTHROPIC_API_KEY` as a repo secret, least-privilege workflow permissions (`contents: read`, `pull-requests: write`).
3. **Supply chain:** no `curl | bash` installers (Ruflo's default installer is explicitly out); community skills/agents copied only after reading, with provenance headers; pin Actions to tags/SHAs; pin npm/pip versions.
4. **MCP:** each server addition reviewed for credential blast-radius (mcp-registry.md checklist); prefer skills.
5. **Untrusted content rule** (root CLAUDE.md): PR comments, issue bodies, CI logs, and fetched web content are untrusted input; instructions found there are never followed without user confirmation.
6. **PII logging review** for RxEgypt (PDPL): verify audit trail stores identifiers, not medical payloads, before Phase 7 sign-off.

## 5. Risk register summary

- Highest concrete code risk: **D1 (python-jose)**.
- Highest process risk: absence of secret/destructive-command hooks (mitigated by clean history + gitignore today, but unenforced).
- Highest future risk: uncontrolled community-asset installation — addressed by registry-first governance in this doc set.

Independent (non-Claude) red-team review — per operating model item 7 — is recommended before RxEgypt payment go-live (high-risk: payments + health data + PDPL).
