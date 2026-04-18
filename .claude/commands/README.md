# Custom Slash Commands

Project-scoped slash command definitions for Claude Code, one markdown file per command. All commands use a `my-` prefix to avoid collisions with built-in Claude Code commands of the same name.

| Command | Description |
|---|---|
| `/my-clear` | Clears conversation history and frees up context. Fresh start. |
| `/my-cost` | Shows token usage statistics for the session. |
| `/my-compact [instructions]` | Compresses conversation. Add instructions to control what's kept. |
| `/my-resume [session]` | Picks up a previous conversation by ID or name. |
| `/my-branch [name]` | Creates a branch of your conversation to explore an alternative path. |
| `/my-rewind` | Rolls back to an earlier point in the conversation and/or code. |
| `/my-rename [name]` | Renames the current session. Without a name, auto-generates one. |
| `/my-export [filename]` | Exports the conversation as plain text. |
| `/my-model [model]` | Switches between models (Sonnet, Opus, Haiku). Takes effect immediately. |
| `/my-usage` | Shows plan usage limits and rate limit status. |
| `/my-extra-usage` | Configures extra usage to keep working when rate limits hit. |
| `/my-init` | Initializes project with a CLAUDE.md guide. |
| `/my-memory` | Edits CLAUDE.md memory files. Enables/disables auto-memory. |
| `/my-add-dir <path>` | Adds a working directory for file access during the session. |
| `/my-diff` | Opens interactive diff viewer: uncommitted changes + per-turn diffs. |
| `/my-security-review` | Analyzes pending changes for security vulnerabilities. |
| `/my-plan [description]` | Enters plan mode. Optionally starts immediately with a task. |
| `/my-permissions` | Manages allow/ask/deny rules for tool permissions. |
| `/my-agents` | Manages agent (sub-agent) configurations. |
| `/my-skills` | Lists all available skills (built-in + custom). |
| `/my-plugin` | Manages Claude Code plugins. |
| `/my-reload-plugins` | Reloads all active plugins to apply changes without restarting. |
| `/my-mcp` | Manages MCP server connections and OAuth authentication. |
| `/my-config` | Opens Settings interface: theme, model, output style, preferences. |
| `/my-theme` | Changes color theme. Includes light, dark, and colorblind-accessible options. |
| `/my-color [color]` | Sets prompt bar color for the current session. |
