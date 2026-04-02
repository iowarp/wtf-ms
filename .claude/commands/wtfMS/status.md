---
name: wtfMS:status
description: Show full research project dashboard — identity, workflow progress, data, and next action
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

<objective>
Display a concise dashboard of the current wtfMS research project. No subagents — reads files directly and formats output.
</objective>

<process>

## 1. Check Initialization

```bash
[ ! -f .research/RESEARCH.md ] && echo "No research project initialized. Run /wtfMS:identify-research to start." && exit 0
```

## 2. Read All State Files

```bash
cat .research/RESEARCH.md
cat .research/LITERATURE.md 2>/dev/null | head -30
cat .research/WORKFLOW.md 2>/dev/null
cat .research/STATE.md 2>/dev/null
cat .research/DATA-INDEX.md 2>/dev/null | head -20
ls .research/tasks/ 2>/dev/null
ls .research/data/ 2>/dev/null
ls .planning/ 2>/dev/null | head -5
```

## 3. Display Dashboard

Format and display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS RESEARCH STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESEARCH IDENTITY
  Prompt:   [research prompt from RESEARCH.md]
  Domain:   [domain + sub-field]
  Stage:    [career stage]

LITERATURE
  Status:   [LITERATURE.md exists? complete | pending]
  Gaps:     [N gaps identified]
  Keywords: [primary keywords]

VIRTUAL LAB
  Status:   [VIRTUAL-LAB.md exists? defined | not defined]
  Equipment:[N items] | Compute: [HPC systems] | Gaps: [N flagged]

WORKFLOW  ([N]/[total] tasks complete)
  Task 01:  [name] — [☑ complete | ☑ in-progress | ☐ pending | ☐ archived]
  Task 02:  [name] — [status]
  ...

DATA
  [N] files registered (.research/DATA-INDEX.md)
  [N] files in .research/data/

PAPER (wtf-p)
  [.planning/PROJECT.md exists? "Paper project initialized" | "Not started — use /wtfMS:wtfp"]

───────────────────────────────────────────
▶ SUGGESTED NEXT ACTION
  [smart routing based on state]
───────────────────────────────────────────
```

## 4. Smart Next Action

Based on state, suggest:
- No RESEARCH.md → `/wtfMS:identify-research`
- No LITERATURE.md → `/wtfMS:literature-review`
- No VIRTUAL-LAB.md → `/wtfMS:define-virtual-lab`
- No WORKFLOW.md → `/wtfMS:define-research-tasks`
- Tasks pending → `/wtfMS:execute-task [next pending N]`
- All tasks complete, no paper → `/wtfMS:wtfp`
- All tasks complete, paper in progress → `/wtfp:progress`

</process>
