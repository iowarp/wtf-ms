---
name: wtfMS:pause-research
description: Pause the current research workflow — saves state and marks active task as paused
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
---

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
