---
description: "Add a new task to the research workflow"
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
Add a new task to WORKFLOW.md through a short interview. Inserts at the end or at a specified position.
</objective>

<context>
No arguments.
</context>

<process>

## 1. Read Current Workflow

```bash
[ ! -f .research/WORKFLOW.md ] && echo "ERROR: No WORKFLOW.md. Run /wtfMS:define-research-tasks first." && exit 1
cat .research/WORKFLOW.md
```

Count current tasks and show the list.

## 2. Gather Task Details

Use ask_user:
- header: "Add Task"
- question: "Define the new task:\n1. **Name**: Short descriptive name\n2. **Type**: literature | experimental | computational | data-analysis | analytical | writing\n3. **Description**: What needs to be done?\n4. **Inputs**: What data or prior task output does this need?\n5. **Expected output**: What will this task produce?\n6. **Position**: After which task? (default: end of list)\n7. **Dependencies**: Which tasks must complete first?"
- options: "Provided all details" | "Guide me through each field"

## 3. Generate New Task Entry

Assign next task number (or insert at specified position, renumbering subsequent tasks). Task numbers are always two digits (Task 07, Task 12) so they match the directory names.

Write the new task block into WORKFLOW.md at the correct position.

## 4. Create Task Directory

```bash
mkdir -p ".research/tasks/task-$(printf '%02d' "$N")"
```

## 5. Record

Only if `commit_research` is true in `.research/config.json`:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/WORKFLOW.md .research/tasks/ && git commit -m "research: add task [NN] — [task name]"
```

</process>

<success_criteria>
- [ ] New task has all required fields
- [ ] Task numbered correctly (no gaps, no duplicates)
- [ ] Task directory created
- [ ] WORKFLOW.md updated; committed only if commit_research is true
</success_criteria>
