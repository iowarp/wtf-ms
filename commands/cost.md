---
name: wtfMS:cost
description: Show token usage and estimated cost per research step, collected passively during normal operation
allowed-tools:
  - Read
  - Bash
---

<objective>
Report how many tokens (and roughly how many dollars) each wtf-MS step has used
so far, from the metrics the Stop hook records during normal operation into
`.research/metrics.jsonl`. Tokens are exact; cost is an estimate.
</objective>

<steps>

1. Render the per-step report:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/wtf-ms/scripts/record_metrics.py --report
   ```

2. Show the table to the user as-is, then add one or two lines of context:
   - Tokens are exact; the dollar figure is an estimate from a per-model price
     table in the script (editable when prices change).
   - A step's total includes the work its subagent did, broken out under
     "of which subagent". Both collection hooks ship with the plugin, so there
     is nothing for the researcher to install.

3. If the report says no metrics are recorded yet, no wtf-MS command has run
   in this project since the plugin was installed. Collection starts on its
   own — see `docs/recording-metrics.md` for how it works.

</steps>

<notes>
This command only reads and reports; it never spends money or calls a model.
Collection itself is passive (the Stop hook), so metrics accrue whether or not
this command is ever run.
</notes>
