---
description: "Pause the current research workflow — saves state and marks active task as paused"
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
Mark the currently in-progress task as paused in WORKFLOW.md, update STATE.md, and save a checkpoint. Safe to run before closing a session.
</objective>

<process>

## 1. Find In-Progress Task

```bash
grep -n "in-progress" .research/WORKFLOW.md 2>/dev/null | head -5
cat .research/STATE.md 2>/dev/null
```

## 2. Update Status

Change `☑ in-progress` to `☐ paused` for the current task in WORKFLOW.md.

Update STATE.md: set status = "paused", record an ISO 8601 timestamp, and note what the next action was going to be.

## 3. Auto-Save Checkpoint

```bash
mkdir -p .research/checkpoints
tar czf ".research/checkpoints/$(date +%Y%m%d-%H%M)-paused-task-[NN].tgz" --exclude='./data' --exclude='./checkpoints' -C .research .
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/WORKFLOW.md .research/STATE.md && git commit -m "research: pause at task [NN] — [task name]" && git tag "wtfms-checkpoint-paused-$(date +%Y%m%d)"
```

## 4. Confirm

Show: "Research paused at Task [NN]: [name]. Resume with `/wtfMS:resume-research`."

</process>

<success_criteria>
- [ ] In-progress task marked as paused
- [ ] STATE.md updated with pause timestamp and next action
- [ ] Checkpoint archive saved; git tag only if commit_research is true
</success_criteria>
