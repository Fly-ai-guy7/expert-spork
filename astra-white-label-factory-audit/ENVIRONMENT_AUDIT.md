# Phase 1 — Environment Audit

**Audited:** 2026-07-15 · **Host:** remote Claude Code container (not the Mac)

## Operating system

| Item | Value |
|---|---|
| OS | Ubuntu 24.04.4 LTS (Linux 6.18.5, x86_64) — **not macOS** |
| Host type | Ephemeral managed cloud container (Claude Code remote execution) |
| macOS version | **not observable from this session** — capture on the Mac |

## Toolchain

| Tool | Version | Notes |
|---|---|---|
| Claude Code | 2.1.210 | running this session |
| Git | 2.43.0 | |
| Node | v22.22.2 | |
| npm | 10.9.7 | |
| pnpm | 10.33.0 | installed, unused by either project |
| yarn | 1.22.22 | installed, unused by either project |
| Python | 3.11.15 | matches RxEgypt's stated 3.11 target; Luxor CI uses 3.12 |
| Docker CLI | 29.3.1 | **daemon not running** in this container |
| GitHub CLI (`gh`) | not available | GitHub access is via the GitHub MCP server, scoped to `fly-ai-guy7/expert-spork` |
| Firebase CLI | not installed | |
| Google Cloud CLI | not installed | |
| Rust / cargo, Bun, Gradle | present (base image) | unused by these projects |

## Duplicate / deprecated tooling

- Three Node package managers are present (npm, pnpm, yarn). Both projects use
  **npm** (`frontend/package-lock.json`) or no JS build at all (RxEgypt
  frontend). No conflict today; standardise on one (npm now, pnpm if/when the
  factory monorepo is created) to avoid lockfile drift.
- No deprecated tooling found in the repository itself. No global tool
  conflicts observable.

## Version-alignment findings

1. **Python skew:** Luxor CI pins 3.12 (`.github/workflows/ci.yml`), RxEgypt
   CI pins 3.11 (`rxegypt-ci.yml`), README says 3.11. Harmless now; align when
   templates are extracted.
2. **Node 20 in CI vs 22 locally.** Vite 5 supports both; record in the
   template's engines field later.

## Secrets exposure scan

A pattern scan for committed keys/tokens/passwords across all tracked file
types returned **no committed secrets**. Details in `SECURITY_FINDINGS.md`.
`.env` files are git-ignored; only `.env.example` templates are committed
(verified: `backend/.env.example`, `frontend/.env.example`,
`rxegypt-pilot/backend/.env.example` contain placeholders only).

## Not observable from this session (to capture on the Mac)

- macOS version, Homebrew inventory, local Docker Desktop status
- Local Claude Code user config (`~/.claude` on the Mac), skills, agents,
  hooks, MCP servers installed there
- Dashy configuration and its service links
- Any tool versions that differ on the Mac
