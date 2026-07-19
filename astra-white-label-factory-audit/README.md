# Astra White-Label Factory — Discovery & Architecture Audit

**Date:** 2026-07-15
**Phase:** Discovery, analysis and architecture proposal (no refactoring performed)
**Auditor:** Claude Code (lead local systems engineer role), remote session

---

## Critical scope note — read this first

This audit was executed inside a **remote Claude Code cloud container**
(Ubuntu 24.04, ephemeral), **not on Bruce's Mac**. The container was
provisioned with a fresh clone of exactly one repository:

- `fly-ai-guy7/expert-spork` → `/home/user/expert-spork`

Consequences, reported honestly rather than papered over:

1. **What could be audited fully:** the two confirmed applications inside
   `expert-spork` — the **Luxor Guest House MVP** (travel/hospitality) and the
   **RxEgypt Pilot** (health/pharmacy compliance) — plus their CI, deployment
   config, design-token contract, tests and security posture.
2. **What could NOT be observed from here:** the Mac's filesystem
   (`~/projects`, `~/Developer`, `~/bruce-os`, etc.), its running localhost
   services (Dashy :8080, Atlas Voyage :4173, the unidentified :3000 service,
   the :8000 collision history), and every named project not present in this
   repo (Atlas Voyage, Voyara, Marina Ember, SafePlate, Founder OS, The Hive,
   etc.). These are recorded in the registries with status `not-observable`
   rather than guessed at.
3. **Nothing was fabricated.** Every score, finding and recommendation in
   these documents is backed by files in this repository, cited by path.

To complete the full local audit, re-run this same brief in a Claude Code
session **on the Mac itself** (CLI or desktop app); the methodology, registry
schemas and document set here are designed to be extended in place.

## Where the audit lives

The requested location `~/bruce-os/astra-white-label-factory-audit` exists in
this container as a symlink to this directory. Because the container is
ephemeral, the durable copy is this directory, committed to branch
`claude/astra-factory-discovery-audit-nybtf4`. It sits at the repository top
level, outside the three application trees (`backend/`, `frontend/`,
`rxegypt-pilot/`), so no application source was touched.

## Document index

| File | Contents |
|---|---|
| `ENVIRONMENT_AUDIT.md` | Phase 1 — toolchain and environment |
| `CLAUDE_CODE_AUDIT.md` | Existing Claude Code config, skills, hooks, MCP |
| `LOCALHOST_SERVICES.md` | Phase 2 — ports and processes |
| `PROJECT_REGISTRY.md` / `project-registry.json` | Phase 3 — all projects |
| `PORT_REGISTRY.md` / `port-registry.json` | Port usage and conflicts |
| `PROJECT_LINEAGE.md` | Phase 4 — relationships between projects |
| `DUPLICATION_REPORT.md` | Repeated patterns across the two apps |
| `REUSABILITY_MATRIX.md` | Phase 5 — reusable capabilities ranked |
| `WHITE_LABEL_READINESS.md` | Phase 6 — hard-coded items per product |
| `CANONICAL_PROJECT_RECOMMENDATIONS.md` | Strongest project per family |
| `PILOT_TEMPLATE_ASSESSMENT.md` | Travel + restaurant pilot evaluation |
| `FACTORY_ARCHITECTURE_PROPOSAL.md` | Phase 7 — target architecture |
| `CLIENT_CONFIG_SCHEMA_PROPOSAL.md` | Configuration-driven client model |
| `CLAUDE_CODE_OPERATING_LAYER.md` | Commands + subagents adoption plan |
| `QA_AUTOMATION_PLAN.md` | Automated QA target for generated clients |
| `SECURITY_FINDINGS.md` | Security review of both apps |
| `MIGRATION_SEQUENCE.md` | Recommended order of work |
| `RISKS_AND_UNKNOWNS.md` | What could go wrong, what is unverified |
| `CURRENT_PRIORITY.md` / `NEXT_ACTION.md` / `PROJECT_STATUS.md` | Live status |

## Executive summary

See the final section of `PROJECT_STATUS.md` and the executive summary posted
in the session reply. Headline: **2 confirmed applications, both
deploy-ready-ish, sharing an already-written design-token contract
(`DESIGN_SYSTEM.md`) that is the natural seed of `packages/design-tokens`. The
Luxor Guest House app is the recommended first white-label pilot** — its
content is already externalised into JSON ledger files, leaving mostly
frontend brand extraction. Both backends default to port 8000, confirming the
known collision risk with repository evidence.
