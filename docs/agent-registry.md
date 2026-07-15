# Astra Agent Registry

Single source of truth for Claude Code subagents in the Astra operating layer.
Format: `.claude/agents/<name>.md` with YAML frontmatter (`name`, `description`, `tools`, optional `model`) — current Claude Code subagent format.
Status flow: `proposed → approved → active → retired`.

**Currently installed agents: none.** Built-in session agents (Explore, Plan, general-purpose, claude-code-guide) exist at the harness level and already cover generic search/plan duties — Astra agents must add Astra-specific policy, not duplicate these.

## Governance rules

1. **Implementer ≠ approver.** Any change produced by an implementing agent requires `independent-validator` (or `/review`) before completion is claimed.
2. Read-only agents get read-only tool lists (no Edit/Write/Bash-write).
3. Parallel agents only for separable tasks.
4. Every agent's `description` must state *when to delegate to it*, precisely — vague descriptions cause wrong autodelegation.
5. One concern per agent; overlapping mandates are the primary instruction-conflict risk and are resolved in this registry before files are written.

## Core set (Phase 4)

| Agent | Status | Mandate | Tools posture |
|---|---|---|---|
| astra-architect | proposed | Architecture decisions, plan coherence, phase gates; guards the authority hierarchy | Read-only + plan output |
| repo-cartographer | proposed | Repository mapping for `/map`; produces the routes/APIs/deps map | Read-only |
| frontend-engineer | proposed | React/Vite (and later Next.js) implementation to AISE UI standard incl. RTL/AR-EN | Full edit |
| backend-engineer | proposed | FastAPI/SQLAlchemy implementation; preserves Rx-gating, PDPL, audit-trail invariants | Full edit |
| test-engineer | proposed | Writes/runs tests alongside implementation; owns honest failure reporting | Full edit + Bash |
| independent-validator | proposed | Post-implementation verification: runs lint/type/tests, exercises the change, approves/rejects. Never implements. | Read + Bash (run-only) |

## Deferred (named reservations)

scope-guardian · product-designer · ui-design-engineer · motion-engineer · data-architect · accessibility-reviewer · security-reviewer · performance-engineer · seo-geo-specialist · devops-engineer · documentation-engineer · commercial-product-reviewer

Activation trigger: first real task that a core agent cannot cover without diluting its mandate. `security-reviewer` and `accessibility-reviewer` are expected first (Phase 5–6).

## Rejected approaches

- **Bulk-installing 0xfurai/claude-code-subagents (100+ agents):** rejected — context bloat, generic mandates overlapping ours, no Astra policy. Use individual files as *format* references only.
- **Ruflo swarm agents:** deferred to Phase 9 isolated evaluation per the multi-agent rules.
