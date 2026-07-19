# Claude Code Configuration Audit

**Scope:** the Claude Code setup visible in this remote session. The Mac's
local `~/.claude` was not reachable and must be audited separately.

## User-level configuration (`/root/.claude` in this container)

| Item | Finding |
|---|---|
| `settings.json` | None — only a harness-managed `launcher-settings.json` (remote-session plumbing, not user config) |
| Skills | 1: `session-start-hook` (harness-provided, for configuring web sessions) |
| Subagents | None user-defined. Harness provides built-in agent types (general-purpose, Explore, Plan, claude-code-guide, statusline-setup) |
| Commands | None user-defined |
| Hooks | Harness-managed only: `session-start-git-identity.sh`, `stop-hook-git-check.sh`, `stop-hook-reply-gate.py`, `user-prompt-submit-reply-reminder.py` — session lifecycle plumbing, not project logic |
| Plugins | None |
| MCP servers | Provisioned by the claude.ai session, not by repo config: GitHub (scoped to `fly-ai-guy7/expert-spork`), Notion, Canva, Figma, Gamma, Slack, Supabase, Vercel, Gmail, Google Drive/Calendar, Shopify, Spotify, Booking.com, Expedia, Tripadvisor, Upwork, PDF Viewer. **Zapier is configured but unauthenticated** (needs authorisation in claude.ai connector settings before use). |

## Project-level configuration

| Item | Finding |
|---|---|
| Root `CLAUDE.md` | **None** at repo root |
| Root `.claude/` | None |
| `.mcp.json` | None |
| `rxegypt-pilot/CLAUDE.md` | **Exists and is good** — repo layout, build-status table, legal shipping flags, AISE branding rules, output conventions. This is the best existing example of project-level Claude configuration and a model for other projects. |

## Instruction conflicts

- None found. The only project instruction file is `rxegypt-pilot/CLAUDE.md`;
  it does not conflict with anything at user level (there is nothing at user
  level).
- Latent risk: `rxegypt-pilot/CLAUDE.md` contains client/company context
  (names, grant targets) that would leak into *other* projects' sessions if it
  were ever moved to the repo root. Keep per-product CLAUDE.md files inside
  their product directories.

## Addendum — user-level skill ecosystem (observed later in session)

After the initial config scan, the session surfaced an extensive **existing
Compound OS™ / AISE skill collection** attached to the user's claude.ai
workspace (not stored in this repo): governance skills
(`compound-os-constitution`, `compound-os-orchestrator`, `skill-governor`,
`governance-reviewer`, `runtime-coordinator`, `knowledge-graph-manager`),
domain skills (`rxegypt`, `hospitality-ai`, `travel-intel`, `equalise-legal`,
`grant-engineering`, `financial-engineer`, `egypt-intelligence`,
`arabic-overlay`, `brand-architect`, `product-strategy-deploy`,
`operator-design`, `hive-systems-architect`, `rex-api-engineer`), and ops
skills (`aise-deploy-monitor`, `project-intake-gate`, `security-ops`,
`sales-pipeline`, `client-delivery`, `people-talent`, `content-media`,
`automation-data`, `strategic-ops`, `digital-twin`, `hrg-arrivals`,
`morning`).

Implications for the proposed operating layer:

1. **A governance layer already exists.** The proposed factory commands must
   register with it, not duplicate it — `runtime-coordinator` and
   `skill-governor` explicitly claim sequencing/overlap-detection authority.
2. **Overlap risk is real:** `rxegypt` (skill) vs `rxegypt-pilot/CLAUDE.md`
   (repo doc) both carry RxEgypt context; `aise-deploy-monitor` names a
   Vercel+Supabase stack while this repo targets Render/Vercel/Fly — a
   **stack-assumption conflict to reconcile** before deployment automation.
3. The `CLAUDE_CODE_OPERATING_LAYER.md` adoption plan therefore proposes the
   minimum *new* commands only, and defers anything `skill-governor` should
   arbitrate.

## Gaps (to fill in a later, authorised phase)

1. No root `CLAUDE.md` describing the two-app repo layout, the port
   assignments, and the "don't cross-edit between Luxor and RxEgypt" rule.
2. No reusable commands or subagents for the factory workflow — the proposed
   minimal set and an adoption plan are in `CLAUDE_CODE_OPERATING_LAYER.md`.
3. The Mac-side Claude Code installation (versions, skills, MCP, memory) is
   unaudited.

**Per the phase rules, nothing was installed or changed.**
