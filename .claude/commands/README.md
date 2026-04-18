# Custom Slash Commands

Project-scoped slash command definitions for Claude Code, one markdown file per command.

| Command | Description |
|---|---|
| `/clear` | Clears conversation history and frees up context. Fresh start. |
| `/cost` | Shows token usage statistics for the session. |
| `/compact [instructions]` | Compresses conversation. Add instructions to control what's kept. |
| `/resume [session]` | Picks up a previous conversation by ID or name. |
| `/branch [name]` | Creates a branch of your conversation to explore an alternative path. |
| `/rewind` | Rolls back to an earlier point in the conversation and/or code. |
| `/rename [name]` | Renames the current session. Without a name, auto-generates one. |
| `/export [filename]` | Exports the conversation as plain text. |
| `/model [model]` | Switches between models (Sonnet, Opus, Haiku). Takes effect immediately. |
| `/usage` | Shows plan usage limits and rate limit status. |
| `/extra-usage` | Configures extra usage to keep working when rate limits hit. |
| `/init` | Initializes project with a CLAUDE.md guide. |
| `/memory` | Edits CLAUDE.md memory files. Enables/disables auto-memory. |
| `/add-dir <path>` | Adds a working directory for file access during the session. |
| `/diff` | Opens interactive diff viewer: uncommitted changes + per-turn diffs. |
| `/security-review` | Analyzes pending changes for security vulnerabilities. |
| `/plan [description]` | Enters plan mode. Optionally starts immediately with a task. |
| `/permissions` | Manages allow/ask/deny rules for tool permissions. |
| `/agents` | Manages agent (sub-agent) configurations. |
| `/skills` | Lists all available skills (built-in + custom). |
| `/plugin` | Manages Claude Code plugins. |
| `/reload-plugins` | Reloads all active plugins to apply changes without restarting. |
| `/mcp` | Manages MCP server connections and OAuth authentication. |
| `/config` | Opens Settings interface: theme, model, output style, preferences. |
| `/theme` | Changes color theme. Includes light, dark, and colorblind-accessible options. |
| `/color [color]` | Sets prompt bar color for the current session. |

Note: many of these names match built-in Claude Code commands. Built-ins take precedence; these project files act as prompt-driven fallbacks and document the intended behavior.
