---
name: wtfMS:add-task
description: Add a new task to the research workflow
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - AskUserQuestion
---

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

Use AskUserQuestion:
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
