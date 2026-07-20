---
name: wtfMS:execute-task
description: Execute a specific research task or the entire workflow
argument-hint: "[task number N, or 'all' for full workflow]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Task
  - AskUserQuestion
---

<execution_context>
@.research/WORKFLOW.md
@.research/RESEARCH.md
@.research/LITERATURE.md
@.research/STATE.md
</execution_context>

<objective>
Execute a specific research task (or the full workflow sequentially) by spawning the appropriate agent based on task type. Updates task status and creates outputs in .research/tasks/task-N/.

**Orchestrator role:** Resolve target task, check dependencies, gate-confirm, spawn wtfms-task-executor with full task context, update WORKFLOW.md status, commit.

**Why subagent:** Each task type (literature, computational, data-analysis, experimental-protocol) requires different reasoning depth. Fresh context per task = focused execution.
</objective>

<context>
Target: $ARGUMENTS (task number, or "all")
</context>

<process>

## 1. Validate Environment

```bash
[ ! -f .research/WORKFLOW.md ] && echo "ERROR: No WORKFLOW.md. Run /wtfMS:define-research-tasks first." && exit 1
cat .research/WORKFLOW.md
cat .research/STATE.md 2>/dev/null
```

## 2. Resolve Target Task

**If $ARGUMENTS is empty:** Find the first task with status `☐ pending` or `☐ in-progress` in WORKFLOW.md.

**If $ARGUMENTS = "all":** Collect all pending tasks in dependency order.

**If $ARGUMENTS = number:** Find that specific task. Verify status and dependencies.

**Dependency check:** If the target task has `Dependencies: Task XX`, verify Task XX is `☑ complete`. If not:
- Warn the user: "Task [N] depends on Task [XX] which is not complete."
- Ask via AskUserQuestion: proceed anyway, or execute Task XX first?

## 3. Show Task Summary

Display the target task entry from WORKFLOW.md:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Task [N]: [name]
 Type:     [literature | computational | experimental | data-analysis | writing]
 Inputs:   [what's needed]
 Outputs:  [what this produces]
 Assumptions: [list]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 4. Gate Check — Confirm Before Executing

Use AskUserQuestion:
- header: "Execute Task [N]: [name]"
- question: "Ready to execute this task?\n\n**Assumptions being made:**\n[list assumptions]\n\n**Expected output:**\n[expected outputs]\n\nAny assumptions wrong or missing data?"
- options: "Proceed" | "Update assumptions first" | "I need to upload data first — /wtfMS:upload-data" | "Skip this task"

## 5. Handle Task Type Routing

**If type = `writing`:**
- Tell user: "This task involves writing. Use `/wtfMS:wtfp` to bridge into wtf-p for paper writing."
- Exit gracefully.

**If type = `experimental`:**
- Spawn task-executor in protocol-generation mode
- Output: experimental protocol document + data recording template

**If type = `literature`:**
- Spawn task-executor in literature-search mode (has WebSearch access)
- Output: literature summary + update to LITERATURE.md

**If type = `computational`:**
- Spawn task-executor in script-generation mode
- Output: analysis/simulation scripts + README for running them

**If type = `data-analysis`:**
- Check for uploaded data in `.research/data/` or `.research/tasks/task-N/`
- Spawn task-executor in analysis mode
- Output: analysis code + figures + results summary

**If type = `analytical`:**
- Spawn task-executor in theoretical mode
- Output: derivations, model equations, validation checks

## 6. Spawn wtfms-task-executor Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► EXECUTING TASK [N]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

```
Task(
  prompt="First, read .claude/agents/wtfMS/task-executor.md for your role.\n\n" + filled_prompt,
  subagent_type="general-purpose",
  description="Execute Task [N]: [name]"
)
```

Filled prompt includes:
- `<task>` — full task entry from WORKFLOW.md
- `<research>` — full RESEARCH.md
- `<literature>` — relevant LITERATURE.md sections
- `<prior_outputs>` — outputs from dependency tasks (if any)
- `<data_files>` — list of uploaded data files
- `<output_dir>` — `.research/tasks/task-[NN]/`

## 7. Handle Executor Return

**`## TASK COMPLETE`:**
- **If the task produced citations** (a `literature` task, or any output with a
  `.bib` file or reference list) — verify them before committing:
  ```bash
  python3 .claude/wtf-ms/scripts/verify_citations.py .research/tasks/task-[NN]/*.bib .research/tasks/task-[NN]/*summary*.md 2>/dev/null || true
  ```
  Advisory (never blocks): drop/replace **NOT_FOUND** citations and re-search,
  surface **MISMATCH** to the user, annotate **UNVERIFIABLE** placeholders. See
  the literature-review command for the full policy.
- Mark task as `☑ complete` in WORKFLOW.md
- Update STATE.md: current task = N+1
- Commit:
  ```bash
  git add .research/tasks/task-[NN]/ .research/WORKFLOW.md .research/STATE.md
  git commit -m "research(task-[N]): [task name] — complete"
  ```

**`## CHECKPOINT REACHED`:**
- Present what's needed (data, decision, domain knowledge) to user
- Collect response, resume executor

**`## TASK BLOCKED`:**
- Show blocker clearly
- Offer: upload missing data, revise assumptions, skip task

**If $ARGUMENTS = "all":** After each task completes, loop to next pending task.

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► TASK [N] COMPLETE ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task:    [N] — [name]
Outputs: .research/tasks/task-[NN]/
Status:  [N]/[total] tasks complete

───────────────────────────────────────────

## ▶ Next Up

**Execute next task**
`/wtfMS:execute-task [N+1]`

**Or check progress**
`/wtfMS:progress`

<sub>`/clear` first → fresh context window</sub>

───────────────────────────────────────────

</offer_next>

<success_criteria>
- [ ] Target task resolved (from argument or next pending)
- [ ] Dependency check completed
- [ ] Gate confirmation always shown with assumptions listed
- [ ] Task type correctly routed to appropriate executor mode
- [ ] Outputs written to .research/tasks/task-NN/
- [ ] WORKFLOW.md status updated
- [ ] STATE.md updated
- [ ] Committed to git
</success_criteria>
