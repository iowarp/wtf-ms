# Recording token metrics during normal use

The plugin's `wtf-ms/scripts/record_metrics.py` logs how many tokens each
research step uses as you work, so `/wtfMS:cost` can show a per-step breakdown. Tokens
are exact; the dollar figure is an estimate. Collection is passive — it runs
from a Claude Code hook, not from a command — so the numbers accrue on their own.

This is separate from the `eval/` benchmark. The benchmark measures steps under
controlled, repeated conditions to catch regressions when the system changes;
this measures your real sessions.

## Collection is automatic

The hooks ship with the plugin in `hooks/hooks.json`, so there is nothing to
install. `Stop` and `SubagentStop` both run
`${CLAUDE_PLUGIN_ROOT}/wtf-ms/scripts/record_metrics.py`, which returns
immediately unless the working directory contains a `.research/` directory.
Projects that do not use wtf-MS are unaffected.

Before wtf-MS was packaged as a plugin these hooks were added by hand to a
project's `.claude/settings.json`. That is no longer possible or necessary: the
script lives inside the installed plugin, not in your project.

`Stop` fires when Claude finishes a turn (the orchestrator); `SubagentStop`
fires when a subagent finishes and hands over the subagent's own transcript. The script reads whichever transcript it's given and appends any new
messages to `.research/metrics.jsonl`. It writes nothing unless `.research/`
exists, so it's inert outside a wtf-MS project, and it swallows its own errors
so a bad run can never interrupt your session.

Both hooks ship together, so a step's total already includes the work its
subagent did.

Then view the report any time:

```
/wtfMS:cost
```

or directly:

```
python3 ${CLAUDE_PLUGIN_ROOT}/wtf-ms/scripts/record_metrics.py --report
```

## What it counts, and what it misses

A message is charged to the most recent `/wtfMS:<step>` invoked in the same
transcript. Work in a transcript that never ran a wtf-MS command is ignored, so
unrelated Claude Code sessions don't pollute the numbers.

Subagents run in their own transcript, which doesn't carry the `/wtfMS:`
command. The `SubagentStop` hook bridges that: it provides both the
subagent's transcript and the parent's, so the subagent's usage is charged to
the command that spawned it. With both hooks installed, a step's total includes
its subagent — the report breaks out how much under "of which subagent". This
matters most for `execute-task`, where the subagent does the bulk of the work.

Two things it still can't see: attribution is only as good as the
invocation-to-subagent link, and cost is an estimate, not the provider's
authoritative number (only tokens are exact).

## Editing the price estimate

Costs come from a small per-model price table (`PRICING`) near the top of
`record_metrics.py`, in dollars per million tokens. Prices change — edit the
table when they do. Because cost is computed at report time from stored token
counts, a price edit re-prices all past records.
