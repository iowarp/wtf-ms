---
description: "Show full research project dashboard — identity, workflow progress, data, and next action"
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
ls .research/handoff/ 2>/dev/null
ls -1t .research/checkpoints/ 2>/dev/null | head -3
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
  [.planning/project.json → "wtf-p 0.6 project initialized" |
   .planning/PROJECT.md → "wtf-p 0.5 project initialized" |
   .research/handoff/ → "Handoff written — paste into wtf-p" |
   "Not started — use /wtfMS:wtfp"]

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
