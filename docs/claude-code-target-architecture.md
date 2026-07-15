# Astra Claude Code Operating Layer — Target Architecture (Phase 2 proposal)

**Status:** Proposed. Nothing here is installed yet. Approval gate: Emma (orchestrator QA) + Bruce (final authority).

---

## 1. Design principles

1. **Smallest reliable system.** Every agent, skill, command, and hook must justify its context cost. Start with a core of ~6 agents / ~6 skills / ~8 commands / 4 hooks; grow only on demonstrated need.
2. **Git is the source of truth — including for the operating layer itself.** Configuration lives in version control, is code-reviewed like code, and is pinned.
3. **Skills over MCP servers** where either would work (MCP servers cost tens of thousands of context tokens at session start; skills load on demand).
4. **No unreviewed third-party execution.** Community assets are copied in after reading, with source commit and licence recorded in the registries — never installed by remote script.
5. **The implementing agent never solely approves its own work** (independent-validator / review command is mandatory before completion claims).
6. The authority hierarchy (Bruce → Emma → Claude Code → GitHub → Notion → Hive → red-team → Gemini) is fixed and restated in the root CLAUDE.md.

## 2. Placement decision: repository, not home directory

The task brief models the layer on `~/.claude/`. In the actual execution environment this is wrong for three reasons:

1. **Ephemerality.** Remote containers are recreated per session; `~/.claude/` is wiped. Anything not committed to git is lost.
2. **Launcher ownership.** `~/.claude/` in this environment already carries launcher-managed hooks (`SessionStart` git identity, `Stop` git check). Writing our own `settings.json`/hooks there risks clobbering or conflicting with the harness.
3. **Reviewability.** A repo-based layer gets PRs, diffs, and history; a home-dir layer is invisible to governance.

**Therefore:**

| Layer | Location | Role |
|---|---|---|
| Project layer | `<repo>/.claude/` + `<repo>/CLAUDE.md` | The real operating layer, per repository |
| Template layer | `astra-claude-template/` (this repo now; its own repo at Phase 8) | Canonical copy stamped into every Astra repo |
| User layer | `~/.claude/` | **Left alone.** On developer workstations (persistent machines) a thin user CLAUDE.md may point at Astra conventions; in remote containers, nothing. |

## 3. Target directory structure (adapted to current Claude Code format)

Adaptations from the brief's example: skills are directories with `SKILL.md` (current format); commands are markdown files under `.claude/commands/`; hooks are **registered in `.claude/settings.json`** with scripts in `.claude/hooks/`; agents are markdown files with YAML frontmatter (`name`, `description`, `tools`, `model`) under `.claude/agents/`.

```
<repo>/
├── CLAUDE.md                          # concise; links out to docs/
├── .claude/
│   ├── settings.json                  # hooks registration + permissions (checked in)
│   ├── agents/                        # PHASE 4 — core six first
│   │   ├── astra-architect.md         #   plan/architecture governor (plan-mode bias)
│   │   ├── repo-cartographer.md       #   read-only repo mapping (Explore-style)
│   │   ├── frontend-engineer.md
│   │   ├── backend-engineer.md
│   │   ├── test-engineer.md
│   │   └── independent-validator.md   #   never the implementer; approves or rejects
│   │   # deferred to need: scope-guardian, product-designer, ui-design-engineer,
│   │   # motion-engineer, data-architect, accessibility-reviewer, security-reviewer,
│   │   # performance-engineer, seo-geo-specialist, devops-engineer,
│   │   # documentation-engineer, commercial-product-reviewer
│   ├── skills/                        # PHASE 4/5 — each = dir with SKILL.md
│   │   ├── astra-repository-intelligence/
│   │   ├── astra-product-planning/
│   │   ├── astra-testing/
│   │   ├── astra-security/
│   │   ├── astra-ui-system/           # Phase 5
│   │   └── astra-documentation/
│   │   # deferred: nextjs-frontend, ux-review, motion-design, api-engineering,
│   │   # data-engineering, visual-qa, accessibility, performance, seo-geo, devops
│   ├── commands/                      # PHASE 4 — core eight
│   │   ├── plan.md  map.md  tests.md  security.md
│   │   ├── review.md  docs.md  handoff.md  deploy.md
│   │   # deferred: audit, build, ui, ux, animate, refactor, api, data,
│   │   # visual-test, accessibility, performance, seo, release
│   └── hooks/                         # PHASE 4 — four scripts, registered in settings.json
│       ├── protect-secrets.sh         # PreToolUse: block writes/commits of .env, keys, tokens
│       ├── prevent-destructive.sh     # PreToolUse(Bash): warn on rm -rf, drop table, force-push
│       ├── validate-before-commit.sh  # PreToolUse(Bash git commit): lint+tests must pass
│       └── completion-gate.sh         # Stop: PROJECT_STATUS freshness check
│       # deferred: format-after-edit (PostToolUse), update-project-status
├── docs/                              # this audit + registries (already created)
└── packages/                          # PHASE 5 — pnpm workspace, seeded from DESIGN_SYSTEM.md
    ├── design-tokens/                 # first: formalize the existing AISE token contract
    ├── ui/                            # shadcn-based, Storybook, RTL + AR/EN, reduced-motion
    ├── motion/                        # Motion-for-React primitives + duration/easing tokens
    ├── forms/                         # React Hook Form + Zod patterns
    └── accessibility/                 # focus, keyboard-nav, ARIA helpers
```

Rationale for the trimmed core: the full 18/16/21 target concentrates instruction risk (overlapping mandates = conflicting agents) and context cost. The deferred items are named now so their eventual files have reserved identities; each is added when a real task first needs it, not speculatively. Registries (`agent-registry.md`, `skill-registry.md`) track proposed → active status.

## 4. Root CLAUDE.md contract

Concise (≤ ~150 lines), containing: product purpose; current scope (two products: Luxor, RxEgypt); architecture + stack per product; repository structure; coding conventions; shared packages; commands; testing requirements; security constraints; deployment approach; known risks; prohibited changes (never rebrand to "AI Solutions Egypt"; never bypass Rx gating or PDPL consent; never commit secrets; no force-push to main); Current Priority; Next Action; and the operating hierarchy. Deep material stays in `docs/` and the existing runbooks. `rxegypt-pilot/CLAUDE.md` remains as the sub-project file (nested CLAUDE.md files compose).

Status-file consolidation rule (resolves audit conflict C3): `PROJECT_STATUS.md` remains the single status document and **contains** the "Current Priority" and "Next Action" sections; `CURRENT_PRIORITY.md` and `NEXT_ACTION.md` are created as thin one-paragraph pointers only if Emma's workflow requires standalone files. `NEXT_ACTIONS.md` (legacy) gets merged into PROJECT_STATUS and removed.

## 5. External adoption (pinned)

| Phase | Adoption | Pinning |
|---|---|---|
| 5 | Playwright, Storybook, shadcn/ui components, Motion, RHF+Zod | exact npm versions in lockfile |
| 6 | anthropics/claude-code-action, anthropics/claude-code-security-review | Action pinned to release tag/SHA; `ANTHROPIC_API_KEY` as repo secret; external-contributor approval required (prompt-injection surface) |
| 9 | ruvnet/ruflo — isolated evaluation in a sandbox repo only | review pinned release; never `curl \| bash` |

Community agent/skill repos (0xfurai, pedronauck, JSONbored, wilwaldon) are **reference material only**; anything copied in is read first, committed with provenance headers (source URL, commit SHA, licence).

## 6. MCP posture

No project-level `.mcp.json` in Phase 3–4. Session connectors (GitHub, Notion, Supabase, etc.) are account-level and already available where authorized. Candidates for later project-level addition are tracked in `mcp-registry.md` with the token-cost warning applied to each.

## 7. Execution phases (unchanged from brief, with gates)

1. ✅ **Audit** (this document set).
2. **Architecture sign-off** — Emma/Bruce approve this document.
3. Minimal native core: root CLAUDE.md + `.claude/settings.json` + status-file consolidation.
4. Core agents (6), skills (6), commands (8), hooks (4).
5. UI/motion/Playwright/Storybook standards + `packages/*` seed (design-tokens first).
6. GitHub Actions: claude-code-action + security review, pinned.
7. Test the layer against `rxegypt-pilot` (representative: bilingual, regulated, tested).
8. Extract `astra-claude-template/` as a reusable stamp.
9. Ruflo evaluation, isolated.
10. Rollout instructions for all active repos.

No phase starts until the previous one's gate is met. Phase 3 does not start until Phase 2 sign-off.
