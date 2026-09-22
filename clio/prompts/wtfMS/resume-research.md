---
description: "Resume research from a paused state — shows current position and suggests next action"
---

<clio_execution>
Use read, ls, find and grep for file inspection, write/edit for state changes,
and bash for the shell blocks below. Treat $ARGUMENTS as operator text: parse the
command's documented arguments, validate task numbers as positive decimal
integers, and quote actual values in shell commands. Derive NN with printf '%02d'
from the decimal task number; use `.research/tasks/task-NN/` consistently.
Each bash call starts independently; bind actual N, NN, OUT, FILE or checkpoint
values in the same call that uses them. Do not assume shell variables persist.
Read reference files named in execution_context; @ paths are references to read,
not already-inlined file content. Keep project state in `.research/`.

For a command with researcher questions, check that ask_user is available
before running any process step that writes files.
Use ask_user(action="ask", max_rounds=24, questions=[{header:"...",
question:"...", options:[{label:"..."}]}]) for every question below. Preserve the
question text and choices, fill contextual brackets, and collect the researcher's
free text. Send at most four related question objects per round. Cancellation
stops dependent work. If ask_user is unavailable, stop at the first interview
gate before writes and report that this command needs an interactive session.
Close a completed interview with ask_user(action="complete", summary="...",
decisions=[{key:"research_decision",value:"the actual settled decision"}]);
record only answers actually supplied. Keep unresolved questions pending.

Run git add, git commit or git tag only after bash grep confirms
'"commit_research": *true' in `.research/config.json`; absent/false disables them.
Never run git init. Check existing git status first; preserve unrelated staged
changes and report a blocked/failed optional record honestly.
</clio_execution>

<objective>
Load research state and resume from the last paused or in-progress task. Equivalent to /wtfp:progress but triggers active resumption.
</objective>

<process>

## 1. Read State

```bash
cat .research/STATE.md 2>/dev/null
cat .research/WORKFLOW.md 2>/dev/null
```

## 2. Find Paused or Next Pending Task

Look for tasks with status `☐ paused` first, then `☐ pending`.

Change `☐ paused` back to `☑ in-progress` if found.

## 3. Show Resumption Context

Display:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► RESUMING RESEARCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research:   [prompt]
Resuming:   Task [N] — [name]
Last saved: [timestamp from STATE.md]

Task context:
[full task block from WORKFLOW.md]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 4. Update STATE.md

Set status = "active", record the resume timestamp. Only if `commit_research` is true in `.research/config.json`:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/WORKFLOW.md .research/STATE.md && git commit -m "research: resume at task [N] — [task name]"
```

## 5. Offer Next Action

Suggest: `/wtfMS:execute-task [N]` to continue, or `/wtfMS:progress` for full overview.

</process>

<success_criteria>
- [ ] Paused task identified and status restored to in-progress
- [ ] Full task context shown to orient the user
- [ ] STATE.md updated
- [ ] Next command clearly offered
</success_criteria>
