# Linting wtf-MS

wtf-MS has no compiled code — its "source" is the markdown command and agent
definitions under `.claude/`, plus templates and references. `scripts/lint.py`
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
| `frontmatter` | error | Missing/invalid YAML frontmatter; missing `name`/`description`; a command whose `name` doesn't match its filename (`wtfMS:<basename>`); an agent whose `name` isn't `wtfms-<slug>`. |
| `task-tool` | error | A command that spawns a subagent via `Task(...)` but omits `Task` from `allowed-tools` — the command can't launch its agent. |
| `static-include` | error | An `@.claude/...` include (template/reference) that doesn't resolve on disk. |
| `agent-path` | error | A `.claude/agents/wtfMS/<x>.md` path referenced in a command body that doesn't exist. Commands spawn agents by injecting this path into a `general-purpose` subagent prompt, so the path is the real dependency. |
| `tool-names` | error | A typo'd tool name in `allowed-tools` (e.g. `Websearch` vs `WebSearch`). |
| `state-include` | warning | An `@.research/...` include naming an unknown state file (typo guard). These files are generated at runtime, so they are **not** existence-checked — only the name is validated against the known set. |
| `help-sync` | warning | Drift between the command files that exist and the commands listed in `help.md`. |

## Extending it

Both allowlists live at the top of `scripts/lint.py`:

- `KNOWN_TOOLS` — add a tool name here when a new Claude Code tool is adopted.
- `KNOWN_STATE_FILES` — add a filename here when the workflow starts writing a
  new top-level `.research/` state file.

New rules go in `check_command` / `check_agent`; call `fnd.error(...)` for
CI-failing issues and `fnd.warn(...)` for advisory ones.
