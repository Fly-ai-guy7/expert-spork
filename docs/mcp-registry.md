# Astra MCP Registry

Single source of truth for MCP server usage in the Astra operating layer.

## Posture

- **No project-level `.mcp.json` exists, and none is added in Phases 3–4.** MCP servers are the most expensive extension type (context cost at session start — community measurement: ~55k tokens for five servers) and the largest third-party attack surface. Default answer is "use a skill instead".
- Session-level connectors are configured at the account level (claude.ai connectors / managed environment), not in this repository, and vary by session. They are *available capability*, not repo configuration.

## Session-provided connectors observed in the managed environment (2026-07-15)

These are account/session-scoped; listed for awareness only. Nothing to install or commit.

| Server | Relevance to Astra | Notes |
|---|---|---|
| GitHub MCP | **High** — the mandated PR/issue/CI interface in remote sessions (no `gh` CLI) | Scoped to the session's authorized repos only |
| Notion MCP | High — Notion is the knowledge registry layer in the operating model | Use for status/decision sync when directed |
| Supabase MCP | Medium — candidate managed DB for RxEgypt durable storage | Changes go straight to remote projects — treat as production |
| Figma MCP | Medium — design handoff for Phase 5 UI work | |
| Vercel MCP | Medium — Luxor frontend deploy target | |
| Slack / Gmail / Google Calendar / Drive | Situational comms | |
| Zapier | **Unauthenticated** — unavailable until the account owner authorizes it in claude.ai connector settings (cannot be done from a non-interactive session) | |
| Canva / Gamma / Shopify / travel connectors etc. | Not relevant to Astra engineering | Ignore |

## Candidate project-level MCP additions (deferred, each needs its own review)

| Candidate | Would provide | Decision |
|---|---|---|
| Playwright MCP | Browser driving for `/visual-test` | **Defer to Phase 5** — first try plain Playwright via Bash (browser pre-installed at `/opt/pw-browsers`); add MCP only if interactive driving is genuinely needed |
| Context7 (live docs) | Framework docs in context | **Defer** — WebFetch covers most needs; re-evaluate on demonstrated failure |
| Ruflo MCP server(s) | Swarm orchestration | **Phase 9 only**, isolated sandbox |

## Review checklist for any future MCP addition

1. Who publishes it; is the package/version pinned?
2. What tools does it expose; what is the session-start token cost?
3. What credentials does it hold, and what is the blast radius if prompt-injected?
4. Could a skill + CLI do the same job?
5. Record the decision here before touching `.mcp.json`.
