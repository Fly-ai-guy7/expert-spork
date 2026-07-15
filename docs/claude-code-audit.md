# Claude Code Environment Audit — Phase 1

**Repository:** `Fly-ai-guy7/expert-spork` · **Branch:** `claude/code-operating-layer-audit-w5eutg`
**Date:** 2026-07-15 · **Status:** Audit only — nothing installed, no code changed.

---

## 1. Machine and tooling

| Tool | Version | Notes |
|---|---|---|
| Claude Code CLI | 2.1.210 | Managed remote execution container (ephemeral) |
| Node.js | v22.22.2 | `/opt/node22/bin/node` |
| npm | 10.9.7 | |
| pnpm | 10.33.0 | Available — good for a future workspace/monorepo |
| yarn | 1.22.22 | Present, unused by any project |
| Python | 3.11.15 | pip 24.0 |
| Docker | 29.3.1 | Daemon availability not tested (audit only) |
| Git | 2.43.0 | |

**Environment character:** this is a Claude Code **remote execution container**, not a developer workstation. The container is recreated per session; the repository is cloned fresh at session start. Anything written outside the repository (including `~/.claude/`) **does not persist between sessions**. This has a direct architectural consequence — see `claude-code-target-architecture.md` §2.

**GitHub access:** no `gh` CLI. Git pushes go through a local authenticated proxy remote. GitHub operations (PRs, issues, CI status) go through the GitHub MCP server, scoped to `Fly-ai-guy7/expert-spork` only.

## 2. Claude Code configuration found

| Item | State |
|---|---|
| User `~/.claude/CLAUDE.md` | **Absent** |
| User `~/.claude/settings.json` | **Absent** (a launcher-managed `launcher-settings.json` exists — see below) |
| Project root `CLAUDE.md` | **Absent** |
| Project `.claude/` (agents/skills/commands/hooks) | **Absent** |
| Project `.mcp.json` | **Absent** |
| Sub-project `rxegypt-pilot/CLAUDE.md` | **Present** — good quality: repo layout, build status, legal flags, priorities, AISE context |
| User skills | One managed skill: `session-start-hook` (environment-provided) |
| Plugins | None installed |
| Hooks | Environment-managed only: `SessionStart` (git identity), `Stop` (git check), reply-gate scripts — all owned by the remote launcher, **must not be modified or clobbered** |
| MCP servers | Session-provided connectors (GitHub, Notion, Supabase, Figma, Vercel, Slack, Gmail, etc.), configured at the account/session level, not in the repo. Zapier connector present but unauthenticated. |

**Conclusion:** there is effectively **no Claude Code operating layer yet**. The only project-authored asset is `rxegypt-pilot/CLAUDE.md`, which is worth preserving as the template model for per-project CLAUDE.md files.

## 3. Repository map

`expert-spork` is a two-product repository:

```
expert-spork/
├── backend/            Luxor Guest House API — FastAPI, JSON ledger data, 11 pytest tests
├── frontend/           Luxor Guest House SPA — React 18 + Vite 5 (JavaScript, NOT TypeScript)
├── database/           bookings.json append store
├── rxegypt-pilot/      RxEgypt pharmacy platform — FastAPI + SQLAlchemy + Alembic backend,
│                       static HTML/JS frontend (AR/EN, RTL), 70 pytest tests, own CLAUDE.md
├── scripts/            smoke_api.sh
├── .github/workflows/  ci.yml (Luxor, path-scoped) + rxegypt-ci.yml (path-scoped, ruff + pytest + JS checks)
├── render.yaml / vercel.json   Deploy blueprints (Render backend, Vercel frontend)
└── *.md                PROJECT_STATUS, TESTING, SECURITY_NOTES, NEXT_ACTIONS, DEPLOYMENT_RUNBOOK,
                        DESIGN_SYSTEM, GO_LIVE_PLAN, DEPLOYMENT_AND_UIUX_PLAN
```

Both products are functional, tested, CI-covered, and near-deployable (Luxor ~85% ready per `PROJECT_STATUS.md`). Working tree is clean; `main` is the default branch.

## 4. Gap vs the Astra standard stack

The declared Astra default stack (Next.js / TypeScript / Tailwind / shadcn-ui / Motion / Storybook / Playwright) is **not present anywhere in this repository**:

| Astra standard | Current reality |
|---|---|
| Next.js + TypeScript | Luxor: React 18 + Vite in plain JS; RxEgypt: static HTML/JS pages |
| Tailwind + shadcn/ui | Hand-written CSS; shared token contract exists (`rxegypt-pilot/frontend/theme.css`, `DESIGN_SYSTEM.md`) |
| Motion for React | None |
| Storybook | None |
| Playwright | None (backend pytest + `node --check` + one JS unit test only) |
| Shared `packages/*` | None — no workspace tooling at all |
| React Hook Form + Zod | None |

**Do not migrate the existing apps to the standard stack as part of this work.** Both apps function and have go-live plans. The standard stack applies to *new* Astra projects via the template; existing apps adopt pieces incrementally (Playwright smoke tests are the highest-value first addition).

## 5. Existing assets worth preserving

1. `rxegypt-pilot/CLAUDE.md` — the best CLAUDE.md model in the estate (structure, build-status table, legal flags, priorities).
2. The **AISE design-token contract** — `DESIGN_SYSTEM.md` + `theme.css` already unify Luxor and RxEgypt; this is the seed of `packages/design-tokens`.
3. Path-scoped CI workflows — a clean pattern for a multi-product repo.
4. Bilingual AR/EN + RTL implementation in `dawai-patient.html` — reference implementation for the Astra i18n/RTL requirement.
5. Project doc set (PROJECT_STATUS, TESTING, SECURITY_NOTES, NEXT_ACTIONS, runbooks) — matches the required Astra project-file templates almost 1:1; formalize rather than replace.
6. RxEgypt security patterns: prod SECRET_KEY boot guard, audit trail, PDPL consent enforcement, server-side Rx gating.

## 6. Conflicts and risks found

| # | Finding | Severity | Detail |
|---|---|---|---|
| C1 | `~/.claude/` is ephemeral and launcher-managed | **High (architectural)** | Building the operating layer at user level, as the task's example structure suggests, would silently vanish every session and risks colliding with launcher hooks. Layer must live in git. |
| C2 | No root CLAUDE.md | Medium | Claude sessions in this repo currently get no repo-wide guidance; `rxegypt-pilot/CLAUDE.md` only loads when working in that directory. |
| C3 | Duplicate/drifting status docs | Low-Medium | `PROJECT_STATUS.md`, `NEXT_ACTIONS.md`, `GO_LIVE_PLAN.md`, `DEPLOYMENT_AND_UIUX_PLAN.md` overlap; the required `CURRENT_PRIORITY.md` / `NEXT_ACTION.md` files would add two more sources of truth unless consolidation rules are set. |
| C4 | `python-jose` dependency (RxEgypt) | **High (security)** | Effectively unmaintained; historical CVEs (algorithm-confusion / JWT issues). Replace with `PyJWT` or `joserfc`. See `security-review.md`. |
| C5 | Unpinned CDN hotlinks risk | Closed | Prior unlicensed photo hotlinks already replaced with bundled placeholders (commit `faa7200`) — pattern to keep enforcing. |
| C6 | CORS allows any `*.vercel.app` (Luxor backend) | Medium | Any Vercel-hosted site can call the API. Acceptable for a demo; tighten before real bookings. |
| C7 | Vite 5.3.1 / FastAPI 0.110–0.111 behind current | Low | Dev-server CVEs exist for old Vite versions (dev-only exposure); schedule routine bumps. |
| C8 | 18-agent / 16-skill / 21-command target in one shot | Medium (context bloat) | Directly conflicts with the "smallest reliable system" mandate. Phase the rollout (see target architecture). |
| C9 | Secrets in config/source | **None found** | `git ls-files` + pattern grep across tracked files: only `.env.example` placeholders and test fixtures. `.gitignore` correctly excludes `.env`. |

## 7. Missing capabilities (summary)

- No root CLAUDE.md, no `.claude/` operating layer, no project skills/agents/commands/hooks.
- No secret-protection, destructive-command, or completion-gate hooks (git history hygiene currently relies on developer discipline plus the launcher's stop-hook).
- No Playwright, Storybook, visual regression, or accessibility testing anywhere.
- No TypeScript, no schema-validated frontend forms.
- No shared `packages/*` workspace; token contract exists only as CSS + markdown convention.
- No dependency scanning (Dependabot/`pip-audit`/`npm audit`) in CI.
- No AI security review on PRs.

## 8. Adoption matrix — approved discovery sources

Verified against live GitHub on 2026-07-15 where marked ✓; otherwise assessed from documented knowledge.

| Source | Purpose | Licence | Maintenance | Decision | Scope |
|---|---|---|---|---|---|
| anthropics/claude-code ✓ | The CLI itself + docs/examples | Anthropic commercial terms (CLI is not OSS) | Active, official | **Reference** — already installed (2.1.210); use docs as the format authority | Global |
| anthropics/claude-plugins-official ✓ | Official plugin marketplace (Apache-2.0 repo) | Active, official | Curated but third-party plugins vary | **Reference now; selective install in Phase 4+** — evaluate individual plugins one at a time | Global |
| anthropics/claude-code-action | GitHub Action running Claude on PRs/issues | MIT | Active, official | **Adopt in Phase 6** — pinned to a release tag; needs API key secret | Astra template + selected repos |
| anthropics/claude-code-security-review ✓ | AI security review Action on PR diffs | MIT | Active, official | **Adopt in Phase 6** — pin version; ⚠ upstream states it is *not hardened against prompt injection*: require approval for external-contributor workflow runs | Astra template + selected repos |
| shadcn-ui/ui | Copy-in component library (Radix + Tailwind) | MIT | Very active | **Adopt in Phase 5** for new Next.js projects — components are vendored code, not a dependency; pin CLI version when generating | Astra template / `packages/ui` |
| motiondivision/motion | Motion for React animation library | MIT | Very active | **Adopt in Phase 5** — pinned npm dependency in `packages/motion` | Astra template |
| microsoft/playwright | Browser/E2E/visual testing | Apache-2.0 | Very active | **Adopt in Phase 5** — Chromium is already pre-installed in this environment (`/opt/pw-browsers`) | Astra template + both existing apps |
| storybookjs/storybook | Component isolation + docs | MIT | Very active | **Adopt in Phase 5** for projects with a component library; **skip** for RxEgypt static pages | Astra template / `packages/ui` |
| 0xfurai/claude-code-subagents ✓ | 100+ generic language/framework subagents (MIT, 957★, ~7 commits, low churn) | MIT | Low activity | **Adapt, don't install** — bulk-installing 100 agents is context bloat and instruction-conflict risk. Mine 2–3 files as *format references* for our own agents | Reference only |
| pedronauck/skills ✓ | 128 curated skills, `npx skills add` installer (500★, licence unclear at root) | Unverified per-skill | Moderate | **Adapt selectively** — never run the installer wholesale; copy individual skills after reading them, pin the source commit, record licence per skill | Reference only |
| JSONbored/awesome-claude ✓ | Registry/catalog of 1,371 Claude assets (MIT, actively maintained) | MIT | Active | **Reference** — discovery index only; everything found through it gets its own review | Reference only |
| wilwaldon/Claude-Code-Frontend-Design-Toolkit ✓ | Curated frontend-quality guide (MIT, 421★, updated Feb 2026) | MIT | Curated list, low churn | **Adapt** — its guidance (skills over MCPs, ~55k token cost of 5 MCP servers, anti-generic-AI-slop direction) directly informs our design skills; do not bulk-install its stacks | Reference only |
| ruvnet/ruflo ✓ | Agent meta-harness / swarm orchestration (MIT, 64k★, v3.30.2 2026-07-14) | MIT | Very active | **Defer to Phase 9, evaluate in isolation** — installs 35 plugins, registers MCP servers, hooks 27 integration points, curl-pipe installer. Exactly what the mandate says not to add until the native core is stable. Never install via `curl | bash`; review the pinned release first | Not adopted |

**Net Phase-3/4 install surface: zero external repos.** The native core is built from first-party Claude Code primitives (CLAUDE.md, skills, agents, hooks in `.claude/`), with external adoption starting only in Phase 5 (UI/test tooling) and Phase 6 (GitHub Actions), each pinned.

## 9. Phase 1 verdict

Environment is clean, minimal, and healthy. The main architectural correction to the task brief: **the operating layer must be repository-based (project `.claude/` + a versioned template), not `~/.claude/`-based**, because this environment's home directory is ephemeral and partially launcher-owned. Full design in `claude-code-target-architecture.md`.
