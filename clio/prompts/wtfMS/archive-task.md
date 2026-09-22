---
description: "Archive a task — moves it to the Archived section of WORKFLOW.md, out of active execution"
argument-hint: "[task number N]"
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

<execution_context>
@.research/WORKFLOW.md
</execution_context>

<objective>
Move a task to the Archived Tasks section of WORKFLOW.md. Archived tasks are preserved for reference but excluded from /wtfMS:execute-task and progress tracking. Preferred over remove-task when the task might be relevant later.
</objective>

<context>
Task number: $ARGUMENTS
</context>

<process>

## 1. Validate

```bash
[ ! -f .research/WORKFLOW.md ] && echo "ERROR: No WORKFLOW.md." && exit 1
[ -z "$ARGUMENTS" ] && echo "ERROR: Provide task number. Usage: /wtfMS:archive-task 3" && exit 1
```

## 2. Show Task and Gather Reason

Display the task entry.

Use ask_user:
- header: "Archive Task [N]: [name]"
- question: "Why are you archiving this task? (This note is saved for future reference)\n\n[full task block]"
- options: "No longer needed for this research" | "Deferred to future work" | "Replaced by another task" | "Resource/time constraint" | "Other reason"

## 3. Move Task to Archived Section

- Change task status to `☐ archived`
- Move the task block from the active Tasks section to the `## Archived Tasks` section in WORKFLOW.md
- Add archive note and reason

## 4. Update Dependencies

If any active task depends on this task, warn user and ask how to handle the dependency.

## 5. Record

Only if `commit_research` is true in `.research/config.json`:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/WORKFLOW.md && git commit -m "research: archive task [N] — [reason]"
```

</process>

<success_criteria>
- [ ] Task moved to Archived section (not deleted)
- [ ] Archive reason recorded
- [ ] Active task list clean
- [ ] Dependencies in other tasks flagged if affected
</success_criteria>
