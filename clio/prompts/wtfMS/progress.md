---
description: "Show research progress with statusline, recent work, and smart routing to next action"
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
@.research/STATE.md
@.research/WORKFLOW.md
@.research/RESEARCH.md
</execution_context>

<objective>
Display a rich progress report with statusline, recent task completions, current position, and routing to the next action. Equivalent to /wtfp:progress but for research workflow.
</objective>

<process>

## 1. Validate

```bash
[ ! -f .research/RESEARCH.md ] && echo "No research project. Run /wtfMS:identify-research." && exit 0
cat .research/STATE.md 2>/dev/null
cat .research/WORKFLOW.md 2>/dev/null
cat .research/RESEARCH.md 2>/dev/null | head -20
```

## 2. Build Statusline

```
WTF-MS ► [N]/[total] tasks ◆ [phase: exploring|reviewing|executing|writing] ► [domain]
```

Display this first, before all other output.

## 3. Calculate Progress Metrics

From WORKFLOW.md, count:
- Total active tasks
- Complete tasks (☑ complete)
- In-progress tasks
- Pending tasks
- Archived tasks

Determine current phase:
- No LITERATURE.md → "exploring"
- LITERATURE.md exists, no WORKFLOW.md → "reviewing"
- WORKFLOW.md exists, tasks pending → "executing"
- All tasks complete → "writing"

## 4. Show Recent Work

Find task output files modified in the last 7 days:
```bash
find .research/tasks/ -newer .research/RESEARCH.md -name "*.md" 2>/dev/null | head -5
```

Show 1-line summary of recent task completions.

## 5. Display Progress Report

```
WTF-MS ► [statusline]

# [Research Prompt]

**Phase:**    [exploring | reviewing | executing | writing]
**Progress:** [████████░░] [N]/[total] tasks
**Domain:**   [domain + sub-field]

## Recent Work
- Task [N] ([name]): [1-line output summary]

## Current Position
[Next pending task or current state]

## Key Decisions Made
[from STATE.md]

## Open Questions
[unresolved assumptions or decisions from WORKFLOW.md]
```

## 6. Route to Next Action

**Phase = exploring:** → `/wtfMS:literature-review`
**Phase = reviewing:** → `/wtfMS:define-virtual-lab` if VIRTUAL-LAB.md is missing, otherwise `/wtfMS:define-research-tasks`
**Phase = executing, task in-progress:** → `/wtfMS:execute-task [N]`
**Phase = executing, next pending task:** → `/wtfMS:execute-task [N+1]`
**Phase = writing:** → `/wtfMS:wtfp` or `/wtfp:progress`

Show the routed command clearly. If the researcher chooses it, follow its prompt flow with the existing context.

</process>

<success_criteria>
- [ ] Statusline displayed first
- [ ] Phase correctly determined
- [ ] Task progress shown with counts and visual bar
- [ ] Recent work summarized
- [ ] Smart routing to next command
</success_criteria>
