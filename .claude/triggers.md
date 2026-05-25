# Scheduled triggers

Prompts for [scheduled triggers](https://code.claude.com/docs/en/claude-code-on-the-web)
on Claude Code on the web. Copy a prompt below into the trigger's prompt
field when configuring it in the web UI.

## Weekly TODO sweep

**Suggested schedule:** weekly (e.g. cron `0 14 * * 1` — Mondays 14:00 UTC).

**Prompt:**

> Search the codebase for TODO comments. If there are none, exit without
> making any changes or commits. Otherwise, pick one that seems
> straightforward, implement it on a new branch named
> `claude/todo-implementation-<short-random-id>`, run any tests in the
> repo, commit with a clear message, push the branch, and open a pull
> request against `main` summarizing the TODO and the change.
