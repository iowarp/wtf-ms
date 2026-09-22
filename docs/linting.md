# Linting wtf-MS

wtf-MS has no compiled code — its "source" is the markdown command and agent
definitions under `commands/` and `agents/`, plus the templates, references, and
guardrail scripts under `wtf-ms/`. `scripts/lint.py`
checks the *deterministic* surface of those files so structural breakage is
caught before it surfaces at runtime (where it's invisible until a command
silently misbehaves).

Run it locally:

```bash
python3 scripts/lint.py
```

Zero dependencies (Python stdlib only). It runs in CI on every push and pull
request via `.github/workflows/lint.yml`. **Errors fail CI; warnings don't.**

## What it checks

| Rule | Severity | Catches |
|------|----------|---------|
| `frontmatter` | error | Missing/invalid YAML frontmatter; missing `name`/`description`; a command whose `name` doesn't match its filename (`wtfMS:<basename>`); an agent whose `name` isn't `wtfms-<slug>` or doesn't match its own filename. Claude Code derives a plugin agent's identity from its filename, so a mismatch makes the agent unspawnable by the `subagent_type` the commands use. |
| `task-tool` | error | A command that spawns a subagent via `Agent(...)` (or the legacy `Task(...)`) but lists neither `Agent` nor `Task` in `allowed-tools`. The command can't launch its agent. |
| `static-include` | error | An `@${CLAUDE_PLUGIN_ROOT}/...` include (template/reference) that doesn't resolve on disk. The variable expands to the plugin root at runtime, which is this repository root. |
| `agent-path` | error | An `agents/<x>.md` path referenced in a command body that doesn't exist. Commands spawn agents by injecting this path into a `general-purpose` subagent prompt, so the path is the real dependency. |
| `tool-names` | warning | A typo'd tool name in a tools declaration (e.g. `Websearch` vs `WebSearch`). A warning, not an error, so a tool rename in Claude Code does not fail CI before the allowlist catches up. |
| `state-include` | warning | An `@.research/...` include naming an unknown state file (typo guard). These files are generated at runtime, so they are **not** existence-checked — only the name is validated against the known set. |
| `help-sync` | warning | Drift between the command files that exist and the commands listed in `help.md`. |

## Tool declarations

Commands declare tools under `allowed-tools`; agents declare them under
`tools`, Claude Code's subagent key (`allowed-tools` is still accepted on an
agent as the legacy spelling, and an agent with no declaration inherits every
tool). Either key may be a YAML list or a comma-separated string such as
`tools: Read, Write, Glob, Grep`. A permission pattern like `Bash(git add:*)`
is checked by its tool name. The same `tool-names` rule applies to both file
types.

The subagent spawn tool is `Agent` in current Claude Code; `Task` is the name
it had before the rename. The linter accepts both spellings everywhere.

## Extending it

Both allowlists live at the top of `scripts/lint.py`:

- `KNOWN_TOOLS` — add a tool name here when a new Claude Code tool is adopted
  (`SPAWN_TOOLS` holds the `Agent`/`Task` pair).
- `KNOWN_STATE_FILES` — add a filename here when the workflow starts writing a
  new top-level `.research/` state file.

New rules go in `check_command` / `check_agent`; call `fnd.error(...)` for
CI-failing issues and `fnd.warn(...)` for advisory ones.
