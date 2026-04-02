---
name: wtfMS:resume-research
description: Resume research from a paused state — shows current position and suggests next action
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

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

```bash
git add .research/WORKFLOW.md .research/STATE.md
git commit -m "research: resume at task [N] — [task name]"
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
