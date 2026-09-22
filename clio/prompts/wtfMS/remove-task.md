---
description: "Remove a task from the research workflow permanently"
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
Permanently remove a task from WORKFLOW.md after user confirmation. Use /wtfMS:archive-task instead if you want to preserve it for reference.
</objective>

<context>
Task number: $ARGUMENTS
</context>

<process>

## 1. Validate

```bash
[ ! -f .research/WORKFLOW.md ] && echo "ERROR: No WORKFLOW.md." && exit 1
[ -z "$ARGUMENTS" ] && echo "ERROR: Provide task number. Usage: /wtfMS:remove-task 3" && exit 1
cat .research/WORKFLOW.md
```

## 2. Show Task and Confirm

Display the full task entry to be removed.

**Check for dependents:** Find any tasks that list this task as a dependency. Warn the user if other tasks depend on the one being removed.

Use ask_user:
- header: "Remove Task [N]: [name]?"
- question: "This will permanently delete Task [N] from WORKFLOW.md.\n\n[full task block]\n\n[If dependents exist: WARNING — Tasks [X, Y] depend on this task. Removing it will break their dependency chain.]\n\nAlternative: `/wtfMS:archive-task [N]` preserves it for reference.\n\nProceed with removal?"
- options: "Yes, remove it" | "Archive it instead" | "Cancel"

## 3. Remove Task from WORKFLOW.md

Edit WORKFLOW.md to remove the task block. Update dependency references in other tasks if needed.

## 4. Record

Only if `commit_research` is true in `.research/config.json`:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/WORKFLOW.md && git commit -m "research: remove task [N] — [task name]"
```

</process>

<success_criteria>
- [ ] Task displayed before removal
- [ ] Dependent tasks warned if applicable
- [ ] User explicitly confirmed removal
- [ ] Task block cleanly removed from WORKFLOW.md
- [ ] Dependency references updated in remaining tasks
</success_criteria>
