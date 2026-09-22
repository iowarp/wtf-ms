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
  - Agent
  - AskUserQuestion
---

<execution_context>
@.research/WORKFLOW.md
@.research/RESEARCH.md
@.research/LITERATURE.md
@.research/STATE.md
@.research/config.json
</execution_context>

<objective>
Execute a specific research task (or the full workflow sequentially) by spawning the task executor with the task's type and context. Verifies outputs on disk, runs advisory guardrails, updates task status, and creates outputs in .research/tasks/task-NN/.

**Orchestrator role:** Resolve target task, check dependencies, gate-confirm assumptions, spawn wtfms-task-executor with full task context, verify outputs exist, run guardrails and surface findings, update WORKFLOW.md and STATE.md, checkpoint, record.

**Why subagent:** Each task type (literature, computational, data-analysis, experimental-protocol) requires different reasoning depth. Fresh context per task = focused execution. The executor never asks the researcher anything; checkpoints come back here.
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
cat .research/DATA-INDEX.md 2>/dev/null
grep -q '"web_search": *false' .research/config.json 2>/dev/null && echo "WEB: disabled by config" || echo "WEB: allowed"
```

## 2. Resolve Target Task

**If $ARGUMENTS is empty:** Find the first task with status `☐ pending` or `☑ in-progress` in WORKFLOW.md.

**If $ARGUMENTS = "all":** Collect all pending tasks in dependency order.

**If $ARGUMENTS = number:** Find that specific task. Verify status and dependencies.

Always derive the two-digit form and the output directory:
```bash
NN=$(printf '%02d' "$N"); OUT=".research/tasks/task-$NN"; mkdir -p "$OUT"; echo "$OUT"
```

**Dependency check:** If the target task has `Dependencies: Task XX`, verify Task XX is `☑ complete`. If not:
- Warn the user: "Task [N] depends on Task [XX] which is not complete."
- Ask via AskUserQuestion: proceed anyway, or execute Task XX first?

## 3. Show Task Summary

Display the target task entry from WORKFLOW.md:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Task [NN]: [name]
 Type:     [literature | computational | experimental | data-analysis | analytical | writing]
 Inputs:   [what's needed]
 Outputs:  [what this produces]
 Assumptions: [list]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 4. Gate Check — Confirm Before Executing

Use AskUserQuestion:
- header: "Execute Task [NN]: [name]"
- question: "Ready to execute this task?\n\n**Assumptions being made:**\n[list assumptions, marking any planner defaults not yet confirmed]\n\n**Expected output:**\n[expected outputs]\n\nAny assumptions wrong or missing data?"
- options: "Proceed" | "Update assumptions first" | "I need to upload data first — /wtfMS:upload-data" | "Skip this task"

If assumptions are updated, write them back to the task entry in WORKFLOW.md before spawning.

## 5. Handle Task Type Routing

**If type = `writing`:**
- Tell user: "This task involves writing. Use `/wtfMS:wtfp` to bridge into wtf-p for paper writing."
- Exit gracefully.

**If type = `experimental`:** protocol-generation mode → protocol document + data recording template + checklist

**If type = `literature`:** literature-search mode → summary + BibTeX + LITERATURE.md updates; supplied materials first, web only if allowed

**If type = `computational`:** script-generation mode → input files + submission script + analysis script + README

**If type = `data-analysis`:** check for registered data in DATA-INDEX.md and `.research/data/`; if none, stop and offer `/wtfMS:upload-data` → analysis code + results summary + figure descriptions

**If type = `analytical`:** theoretical mode → derivation, validation, optional implementation

## 6. Spawn wtfms-task-executor Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► EXECUTING TASK [NN]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use the Agent tool with `subagent_type: wtfms-task-executor` and `description: "Execute Task [NN]: [name]"`. The prompt carries:
- `<task>` — full task entry from WORKFLOW.md (with any updated assumptions)
- `<research>` — full RESEARCH.md
- `<literature>` — relevant LITERATURE.md sections
- `<virtual_lab>` — the relevant equipment and software rows from VIRTUAL-LAB.md, if it exists
- `<prior_outputs>` — outputs from dependency tasks (paths and SUMMARY.md contents)
- `<data_files>` — DATA-INDEX.md entries and paths under `.research/data/`
- `<web_allowed>` — true or false from Step 1
- `<output_dir>` — `.research/tasks/task-[NN]/`

## 7. Handle Executor Return

**`## TASK COMPLETE`:**

1. Verify outputs on disk. Self-report is not completion:
   ```bash
   ls -la .research/tasks/task-[NN]/
   test -s .research/tasks/task-[NN]/task-[NN]-SUMMARY.md && echo "SUMMARY OK" || echo "ERROR: no summary"
   ```
   Every file the executor listed under Outputs must exist and be non-empty. If any is missing, resume the agent naming the missing file; do not mark the task complete.

2. Advisory guardrails. Run what applies, read the findings, and surface them; nothing here deletes or rewrites on its own. Skip silently if a script or python3 is missing.
   - Physical sanity, all task types:
     ```bash
     python3 ${CLAUDE_PLUGIN_ROOT}/wtf-ms/scripts/check_physics.py .research/tasks/task-[NN]/*.md 2>/dev/null || true
     ```
   - Citations, if the task produced a `.bib` or reference list:
     ```bash
     python3 ${CLAUDE_PLUGIN_ROOT}/wtf-ms/scripts/verify_citations.py .research/tasks/task-[NN]/*.bib .research/tasks/task-[NN]/*summary*.md 2>/dev/null || true
     ```
   - Generated scripts, if the task produced `.py` or `.sh`:
     ```bash
     python3 ${CLAUDE_PLUGIN_ROOT}/wtf-ms/scripts/check_scripts.py .research/tasks/task-[NN]/*.py .research/tasks/task-[NN]/*.sh 2>/dev/null || true
     ```
   If any finding is **IMPOSSIBLE** (physics), **NOT_FOUND** / **MISMATCH** (citations), or **WILL NOT RUN** (scripts): show the findings to the researcher and ask via AskUserQuestion:
   - header: "Guardrail Findings — Task [NN]"
   - question: "[N] findings:\n\n1. [file:line] [finding] → [suggested fix or closest Crossref match]\n2. ...\n\nHow should I handle them?"
   - options: "Fix them — resume the executor" | "They're fine — note and continue" | "I'll decide per finding"
   Resume the executor with the accepted fixes when asked. Warnings (IMPLAUSIBLE, UNVERIFIABLE, SUSPECT) are listed in the completion output and noted in the task SUMMARY, not gated.

3. Mark task as `☑ complete` in WORKFLOW.md. Update STATE.md: current task = next pending, last completed = [NN].

4. Checkpoint if `auto_checkpoint` is true (default):
   ```bash
   grep -q '"auto_checkpoint": *false' .research/config.json 2>/dev/null || { mkdir -p .research/checkpoints; tar czf ".research/checkpoints/$(date +%Y%m%d-%H%M)-after-task-[NN].tgz" --exclude='./data' --exclude='./checkpoints' -C .research . ; }
   ```

5. Optional git record:
   ```bash
   grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/tasks/task-[NN]/ .research/WORKFLOW.md .research/STATE.md && git commit -m "research(task-[NN]): [task name] — complete"
   ```

**`## CHECKPOINT REACHED`:**
- Present what's needed (data, decision, domain knowledge) via AskUserQuestion
- Resume the same executor agent with a `<resume>` block containing the answer (or re-spawn with the full context plus `<resume>`)

**`## TASK BLOCKED`:**
- Show blocker clearly
- Offer via AskUserQuestion: upload missing data, revise assumptions, execute the blocking task first, or skip this task

**If $ARGUMENTS = "all":** After each task completes, loop to the next pending task. Stop the loop at any CHECKPOINT or BLOCKED return and at the first `writing` task.

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► TASK [NN] COMPLETE ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task:    [NN] — [name]
Outputs: .research/tasks/task-[NN]/ ([N] files, verified)
Guardrails: [N] findings resolved, [N] warnings noted
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
- [ ] Target task resolved (from argument or next pending); two-digit directory used
- [ ] Dependency check completed
- [ ] Gate confirmation always shown with assumptions listed
- [ ] Task type correctly routed; web availability passed explicitly
- [ ] Outputs verified on disk with ls and test -s before marking complete
- [ ] Guardrail findings surfaced to the researcher; nothing auto-removed
- [ ] WORKFLOW.md and STATE.md updated
- [ ] Checkpoint saved if auto_checkpoint; commit only if commit_research is true
</success_criteria>
