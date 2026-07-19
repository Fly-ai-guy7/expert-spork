# Mac Discovery Runbook — Step 0

Purpose: complete the ~30% of the audit that was physically unreachable from
the remote session. Run this **on the Mac**, in a Claude Code session (CLI or
desktop app). Read-only throughout — same safety rules as the original brief
(no installs, no process kills, no file moves, no Dashy changes, never print
secret values).

## How to run it

1. On the Mac: `cd` anywhere, start Claude Code, and clone/pull this branch:
   ```bash
   git clone https://github.com/Fly-ai-guy7/expert-spork.git   # or git pull
   git checkout claude/astra-factory-discovery-audit-nybtf4
   ```
2. Paste the prompt in the box below. It instructs the session to extend the
   registries in `astra-white-label-factory-audit/` in place and push to the
   same branch.

## The prompt (paste verbatim)

```text
You are completing Step 0 of the Astra White-Label Factory audit. The remote
audit lives in astra-white-label-factory-audit/ on this branch — read its
README.md, RISKS_AND_UNKNOWNS.md (U1–U7), and the checklists in
LOCALHOST_SERVICES.md and DUPLICATION_REPORT.md before starting.

Rules: read-only discovery. Do not install anything, kill or restart any
process, move/rename/delete anything, modify Dashy, or print secret values.

Tasks:
1. ENVIRONMENT: record macOS version, Homebrew presence, tool versions
   (git, node, npm, pnpm, yarn, python3, docker + daemon status, gh + auth
   status, firebase, gcloud, claude), and the Mac's ~/.claude configuration
   (settings, skills, agents, commands, hooks, MCP servers — names only).
   Append a "Mac addendum" section to ENVIRONMENT_AUDIT.md and
   CLAUDE_CODE_AUDIT.md.
2. LOCALHOST: run `lsof -nP -iTCP -sTCP:LISTEN`; for each listener capture
   port, PID, process name, working directory (lsof -p <pid> | grep cwd),
   repo association, framework, expectedness, orphan status. Specifically
   resolve: what is on 3000; confirm Dashy on 8080; confirm Atlas Voyage on
   4173; note anything on 8000. If Dashy's config file is readable, list
   which services it links (do not edit it). Update LOCALHOST_SERVICES.md,
   PORT_REGISTRY.md and port-registry.json (move entries from
   macSideClaimsUnverified to observed).
3. PROJECT DISCOVERY: scan ~/projects ~/Projects ~/Developer ~/development
   ~/dev ~/Documents ~/Desktop ~/bruce-os ~/Sites for repos (.git,
   package.json, pyproject.toml, Dockerfile, README.md, CLAUDE.md …). For
   every repo found, add or update an entry in project-registry.json using
   the existing entries as the field template (identity, technical profile,
   quality scores where inspectable, risks). Move any located project out of
   namedButNotObservable. Do not omit projects with incomplete info — mark
   fields "unknown".
4. PRIORITY TARGETS: Atlas Voyage / Voyara (travel pilot donor decision) and
   Marina Ember (restaurant pilot donor decision) get full profiles + the
   lineage checks from DUPLICATION_REPORT.md against luxor-guest-house.
   Also check for standalone forks of Luxor or RxEgypt.
5. WRITE-UP: update CANONICAL_PROJECT_RECOMMENDATIONS.md,
   PILOT_TEMPLATE_ASSESSMENT.md, RISKS_AND_UNKNOWNS.md (resolve U1–U7 where
   possible), CURRENT_PRIORITY.md, NEXT_ACTION.md and PROJECT_STATUS.md
   (raise the completion percentage honestly).
6. Commit to this same branch with a clear message and push. Do not commit
   changes to any application source. Finish with an executive delta
   summary: what changed vs the remote audit's provisional conclusions —
   especially the travel-template donor recommendation.
```

## Expected outputs

- Complete `project-registry.json` (every real repo on the Mac, classified
  or honestly marked unknown) and observed `port-registry.json`.
- Final answers on U1–U7, and a confirmed-or-revised pilot plan.
- The decisions gate (`MIGRATION_SEQUENCE.md` Step 1) becomes runnable.

## Time budget

~Half a day. If the estate is much larger than expected, the prompt's task 3
can be split across sessions — the registry merges incrementally.
