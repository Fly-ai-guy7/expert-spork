# Astra Skill Registry

Single source of truth for skills in the Astra Claude Code operating layer.
**Rule:** a skill exists here before it exists on disk. Status flow: `proposed → approved → active → retired`.
Format: each skill is a directory under `.claude/skills/<name>/` containing `SKILL.md` (current Claude Code format; frontmatter `name` + `description` drives autoload matching).

**Currently installed skills: none (project level).** The only user-level skill present (`session-start-hook`) is environment-managed and out of scope.

## Core set (Phase 4)

| Skill | Status | Purpose | Overlap/conflict notes |
|---|---|---|---|
| astra-repository-intelligence | proposed | Map routes, components, APIs, data stores, deps, deployment before any change; powers `/map` | Keep read-only; overlaps `repo-cartographer` agent — skill holds the method, agent holds the delegation |
| astra-product-planning | proposed | Plan-first workflow: scope read, reuse search, risk list, Current Priority + Next Action; powers `/plan` | Must not duplicate root CLAUDE.md workflow text — reference it |
| astra-testing | proposed | Highest-value-test selection, pytest/Vitest/Playwright patterns, honest failure reporting; powers `/tests` | Subsumes visual-qa until Phase 5 |
| astra-security | proposed | Attack-surface review of changed code: auth boundaries, CORS, secrets, uploads, PII logging; powers `/security` | Complements (not replaces) CI security-review Action |
| astra-documentation | proposed | PROJECT_STATUS/README/DECISIONS upkeep, handoff notes; powers `/docs` + `/handoff` | Owns the status-file consolidation rule |
| astra-ui-system | proposed (Phase 5) | AISE tokens, shadcn usage, RTL/AR-EN, states (loading/empty/error), responsive, no generic AI-gradient styling | Seeded from existing `DESIGN_SYSTEM.md` + `theme.css` |

## Deferred (named reservations — add on first real need)

| Skill | Trigger to activate |
|---|---|
| astra-nextjs-frontend | First Next.js project starts |
| astra-ux-review | First `/ux` request on a live app |
| astra-motion-design | First animation task after `packages/motion` exists |
| astra-api-engineering | First new API surface beyond existing FastAPI apps |
| astra-data-engineering | First schema/migration-heavy task |
| astra-visual-qa | Playwright screenshot baselines exist (Phase 5) |
| astra-accessibility | First a11y audit task (pair with axe/Playwright) |
| astra-performance | First performance budget task |
| astra-seo-geo | First public marketing-site task |
| astra-devops | First multi-environment deploy beyond Render/Vercel/Fly runbooks |

## Provenance rules for adapted community skills

Any skill copied/adapted from pedronauck/skills, awesome-claude listings, or the Frontend Design Toolkit must carry a header: source URL, source commit SHA, licence, date reviewed, and what was changed. Bulk installers (`npx skills add …`) are prohibited.
