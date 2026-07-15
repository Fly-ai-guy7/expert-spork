# Astra Hook Registry

Single source of truth for Claude Code hooks in the Astra operating layer.
Format: shell/python scripts in `.claude/hooks/`, **registered in `.claude/settings.json`** under the `hooks` key (current Claude Code format: event → matcher → command). Hooks are committed and code-reviewed like any code.

## Existing hooks (environment-managed — DO NOT MODIFY)

The remote launcher owns `~/.claude/launcher-settings.json` with:

| Event | Script | Purpose |
|---|---|---|
| SessionStart | `session-start-git-identity.sh` | Git identity setup |
| Stop | `stop-hook-git-check.sh` | Uncommitted-work check at turn end |
| (support) | `stop-hook-reply-gate.py`, `user-prompt-submit-reply-reminder.py` | Harness reply gating |

**Constraint:** project hooks in `<repo>/.claude/settings.json` merge with (never replace) these. Never write to `~/.claude/` in remote sessions.

## Core set (Phase 4) — proposed

| Hook script | Event / matcher | Behaviour | Failure mode |
|---|---|---|---|
| protect-secrets.sh | PreToolUse → Write\|Edit\|Bash | Block writes of `.env` (non-example), private keys, JWTs, cloud credentials; block `git add`/commit of same patterns | **Block** (exit 2) with explanation |
| prevent-destructive.sh | PreToolUse → Bash | Flag `rm -rf` on major dirs, `DROP TABLE`/`TRUNCATE`, `git push --force` (allow `--force-with-lease` on non-main), `git reset --hard`, deploy from dirty tree | **Block**, require explicit user authorization |
| validate-before-commit.sh | PreToolUse → Bash `git commit` | Run scoped lint (+fast tests where cheap) for the touched product (Luxor vs rxegypt-pilot path scoping, mirroring CI) | **Warn/block** on lint failure |
| completion-gate.sh | Stop | If source files changed this session but PROJECT_STATUS.md / Current-Priority section untouched, remind before ending | **Warn** (non-blocking) |

## Deferred

| Hook | Event | Trigger to activate |
|---|---|---|
| format-after-edit.sh | PostToolUse → Edit\|Write | Once formatters are standardized (ruff format / prettier config committed) |
| update-project-status.sh | Stop | If completion-gate proves insufficient; auto-drafting status edits needs care to avoid noise |
| dependency-scan | PreToolUse on lockfile changes | Phase 6, alongside CI scanning (prefer CI: Dependabot + pip-audit + npm audit) |

## Design rules

1. Hooks must be fast (<2s typical) — they run on every matched tool call.
2. Block only on high-confidence matches; prefer warn+confirm for heuristics (false-positive blocks train people to disable hooks).
3. Every hook has a one-line bypass documented for genuine emergencies, requiring explicit human authorization in the session.
4. Hook scripts take no network actions and read no secrets.
5. Test hooks with a fixture transcript before activating (Phase 7 validation includes deliberate trigger attempts).
