# Claude Code Operating Layer — Proposal & Adoption Plan

**Constraint honoured:** nothing was installed this phase. This is a plan.

**Context that changes the plan:** the user's claude.ai workspace already
carries a large Compound OS™ skill ecosystem, including governance skills
(`runtime-coordinator`, `skill-governor`, `governance-reviewer`) and domain
skills (`rxegypt`, `hospitality-ai`, etc.) — see the addendum in
`CLAUDE_CODE_AUDIT.md`. The factory layer must therefore be **small, repo-
scoped, and registered with the existing governance skills**, not a parallel
empire. Several proposed subagents from the brief are already covered by
existing skills and should NOT be rebuilt.

## Minimum command set (repo-level `.claude/commands/`, build in this order)

| Order | Command | Purpose | Seed evidence |
|---|---|---|---|
| 1 | `/discover-local` | Re-run this audit's discovery on any machine; extend `registry/projects.json` + `ports.json` | This audit's methodology; needed first on the Mac |
| 2 | `/map-project` | Deep-profile one repo into a registry entry (identity → quality scores) | `PROJECT_REGISTRY.md` template |
| 3 | `/validate-config` (added; not in brief) | Run the client-schema validator | `CLIENT_CONFIG_SCHEMA_PROPOSAL.md` rules |
| 4 | `/extract-template` | Guided extraction of a project into `templates/<id>` with a hard-coded-item checklist | `WHITE_LABEL_READINESS.md` inventories |
| 5 | `/create-white-label` | Scaffold `clients/<id>/` from template + config; never copies template source | Factory equation |
| 6 | `/production-qa` | Run the full QA pipeline; write report + screenshots to `qa/` | `QA_AUTOMATION_PLAN.md` |
| 7 | `/register-project` | Update registries (+ Dashy sync **only when a later phase authorises writing to Dashy**) | registry JSONs |
| 8 | `/release-client` | Build, deploy, health-check, record in `registry/deployments.json` | runbooks + smoke script |
| 9 | `/handoff` | Produce an Emma/Bruce-readable status pack (current state, decisions needed) | This audit's status docs |

## Subagents — adopt-vs-defer against the brief's list of 19

**Adopt as factory subagents (5, phased):**

| Subagent | Why a dedicated agent is justified | Phase |
|---|---|---|
| repository-mapper | Feeds `/discover-local` + `/map-project`; pure read-only | A |
| scope-controller | Enforces the stop-conditions/no-refactor rules that this phase relied on manually | A |
| production-qa | Runs the QA matrix; must be independent of the code-writing session | B |
| visual-qa | Screenshot + visual-regression review (EN + AR RTL) | B |
| independent-validator | Second-model review before release (per operating hierarchy #8) | C |

**Cover with existing skills instead of new agents:** architecture + scope
governance (`compound-os-constitution`, `governance-reviewer`), product
design (`brand-architect`, `product-strategy-deploy`), security
(`security-ops`), deployment/DevOps (`aise-deploy-monitor` — after the
stack-assumption conflict noted in `CLAUDE_CODE_AUDIT.md` is reconciled),
documentation (`doc-coauthoring`), domain review (`rxegypt`,
`hospitality-ai`, `arabic-overlay` for AR/RTL).

**Defer indefinitely** (no current workload to justify them): dedicated UI
engineering, UX review, motion, frontend, backend, data-architecture, a11y,
performance, SEO/GEO agents — these are roles a single Claude Code session
performs fine at current portfolio size; create an agent only when a command
needs to delegate that role repeatedly.

## Repo-level configuration to add (next authorised phase)

1. Root `CLAUDE.md` for `expert-spork`: two-app layout, port assignments,
   "never cross-edit Luxor/RxEgypt", pointer to this audit.
2. `.claude/commands/` with commands 1–3 only (discover, map, validate) —
   the rest land with the factory workspace itself.
3. No MCP additions; no community skill packs (explicitly out of scope).

## Adoption sequence

- **Phase A (with Mac audit):** commands 1–2 + repository-mapper +
  scope-controller. Exit: complete Mac-side registry.
- **Phase B (with pilot 1):** commands 3–6 + the two QA agents. Exit: Luxor
  client instance passes `/production-qa`.
- **Phase C (first release):** commands 7–9 + independent-validator. Exit:
  registered, deployed, health-checked client.
