---
name: wtfMS:remove-task
description: Remove a task from the research workflow permanently
argument-hint: "[task number N]"
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

Use AskUserQuestion:
- header: "Remove Task [N]: [name]?"
- question: "This will permanently delete Task [N] from WORKFLOW.md.\n\n[full task block]\n\n[If dependents exist: WARNING — Tasks [X, Y] depend on this task. Removing it will break their dependency chain.]\n\nAlternative: `/wtfMS:archive-task [N]` preserves it for reference.\n\nProceed with removal?"
- options: "Yes, remove it" | "Archive it instead" | "Cancel"

## 3. Remove Task from WORKFLOW.md

Edit WORKFLOW.md to remove the task block. Update dependency references in other tasks if needed.

## 4. Commit

```bash
git add .research/WORKFLOW.md
git commit -m "research: remove task [N] — [task name]"
```

</process>

<success_criteria>
- [ ] Task displayed before removal
- [ ] Dependent tasks warned if applicable
- [ ] User explicitly confirmed removal
- [ ] Task block cleanly removed from WORKFLOW.md
- [ ] Dependency references updated in remaining tasks
</success_criteria>
