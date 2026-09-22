---
description: "Execute a specific research task or the entire workflow"
argument-hint: "[task number N, or 'all' for full workflow]"
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

<clio_dispatch>
Select the named recipe with dispatch({agent:"wtfms-...", task:"assignment with
full context and exact permitted outputs", intent:{write_roots:["exact/output"]}}).
Replace the illustrative recipe/path with those stated in this command. Use the
registered dispatch fields shown here.
Read the recipe's bound skill references and inline required templates, domain
sections, answers and selected state into the worker task. Each dispatch starts
fresh: re-dispatch with the full original context, prior candidates/outputs and
the new selection, corrections, revisions or resume answer. Use monitor if the
returned run is still active. Do not infer a resumed transcript from a run ID.
Honor admission refusals instead of broadening write scope.

Agent returns are mutation-report JSON. Route on the beginning of summary using
the status branches below. For checkpoints, distinguish
`needs_input: checkpoint:decision` from `needs_input: checkpoint:human-action`;
ask the exact question(s), collect the answer and re-dispatch. No new top-level
status fields are allowed. A conforming JSON result is not proof of completion.
After EVERY dispatch that wrote, use ls and read on every reported output and on
the command's required files, including loop_back and partial checkpoint returns.
Verify nonempty content and the promised changes before presenting success or
continuing; re-dispatch with any missing/incorrect file named. Treat actual failed
validation or execution as failure even when summary claims completion.
</clio_dispatch>

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

Worker write scope: the selected .research/tasks/task-NN/; include .research/LITERATURE.md only for an approved literature update.


## 1. Inspect Supplied Materials First

Use ls on `.research/data/` and read `.research/DATA-INDEX.md` before other
research inputs. For literature tasks, inspect these registered materials before
fetching anything. Clio has no web search tool: build literature work from
supplied materials plus specific researcher-provided URLs. Request URLs with the
task confirmation if more coverage is needed. Honor web_search false by staying
with supplied materials and record coverage in Sources Reviewed in each summary
and any LITERATURE.md update.

### Validate Environment

```bash
[ ! -f .research/WORKFLOW.md ] && echo "ERROR: No WORKFLOW.md. Run /wtfMS:define-research-tasks first." && exit 1
cat .research/WORKFLOW.md
cat .research/STATE.md 2>/dev/null
cat .research/DATA-INDEX.md 2>/dev/null
grep -q '"web_search": *false' .research/config.json 2>/dev/null && echo "WEB: disabled by config" || echo "URL FETCH: allowed"
```

## 2. Resolve Target Task

**If $ARGUMENTS is empty:** Find the first task with status `☐ pending` or `☑ in-progress` in WORKFLOW.md.

**If $ARGUMENTS = "all":** Collect all pending tasks in dependency order.

**If $ARGUMENTS = number:** Find that specific task. Verify status and dependencies.

Always derive the two-digit form and the output directory:
```bash
# Bind N to the validated decimal task number in this call.
NN=$(printf '%02d' "$N"); OUT=".research/tasks/task-$NN"; mkdir -p "$OUT"; echo "$OUT"
```

**Dependency check:** If the target task has `Dependencies: Task XX`, verify Task XX is `☑ complete`. If not:
- Warn the user: "Task [N] depends on Task [XX] which is not complete."
- Ask via ask_user: proceed anyway, or execute Task XX first?

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

Use ask_user:
- header: "Execute Task [NN]: [name]"
- question: "Ready to execute this task?\n\n**Assumptions being made:**\n[list assumptions, marking any planner defaults not yet confirmed]\n\n**Expected output:**\n[expected outputs]\n\nAny assumptions wrong or missing data?"
- options: "Proceed" | "Update assumptions first" | "I need to upload data first — /wtfMS:upload-data" | "Skip this task"

If assumptions are updated, write them back to the task entry in WORKFLOW.md before spawning.

## 5. Handle Task Type Routing

**If type = `writing`:**
- Tell user: "This task involves writing. Use `/wtfMS:wtfp` to bridge into wtf-p for paper writing."
- Exit gracefully.

**If type = `experimental`:** protocol-generation mode → protocol document + data recording template + checklist

**If type = `literature`:** supplied-corpus and provided-URL review mode → summary + BibTeX + LITERATURE.md updates; supplied materials first, provided-URL fetching only if allowed

**If type = `computational`:** script-generation mode → input files + submission script + analysis script + README

**If type = `data-analysis`:** check for registered data in DATA-INDEX.md and `.research/data/`; if none, stop and offer `/wtfMS:upload-data` → analysis code + results summary + figure descriptions

**If type = `analytical`:** theoretical mode → derivation, validation, optional implementation

## 6. Spawn wtfms-task-executor Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► EXECUTING TASK [NN]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use dispatch with `agent: "wtfms-task-executor"` and a task containing the assignment and full context. The prompt carries:
- `<task>` — full task entry from WORKFLOW.md (with any updated assumptions)
- `<research>` — full RESEARCH.md
- `<literature>` — relevant LITERATURE.md sections
- `<virtual_lab>` — the relevant equipment and software rows from VIRTUAL-LAB.md, if it exists
- `<prior_outputs>` — outputs from dependency tasks (paths and SUMMARY.md contents)
- `<data_files>` — DATA-INDEX.md entries and paths under `.research/data/`
- `<web_allowed>` — true only when config permits URL fetching and web_fetch is available
- `<provided_urls>` — the researcher's specific URLs, or none
- `<output_dir>` — `.research/tasks/task-[NN]/`

## 7. Handle Executor Return

**`task_complete:`:**

1. Use ls and read on every reported output and task-NN-SUMMARY.md. Verify outputs on disk. Self-report is not completion:
   ```bash
   ls -la .research/tasks/task-[NN]/
   test -s .research/tasks/task-[NN]/task-[NN]-SUMMARY.md && echo "SUMMARY OK" || echo "ERROR: no summary"
   ```
   Every file the executor listed under Outputs must exist and be non-empty. If any is missing, re-dispatch the agent naming the missing file; do not mark the task complete.

2. Advisory guardrails. Run what applies, read the findings, and surface them; nothing here deletes or rewrites on its own. Skip silently if a script or python3 is missing.
   Use bash to collect only existing files and keep stderr visible. The scripts
   accept files, not directory arguments; never mistake a skipped file for a
   successful scan. All findings remain advisory. Run these shell blocks only
   after deriving OUT as the selected task directory:
   ```bash
   if command -v python3 >/dev/null 2>&1; then
     shopt -s nullglob globstar
     physics_files=("$OUT"/**/*.md)
     citation_files=("$OUT"/**/*.bib "$OUT"/**/*summary*.md "$OUT"/**/*SUMMARY*.md)
     script_files=("$OUT"/**/*.py "$OUT"/**/*.sh)
     citation_flags=()
     grep -q '"web_search": *false' .research/config.json 2>/dev/null && citation_flags=(--offline)
     ((${#physics_files[@]})) && python3 "${extensionRoot}/resources/scripts/check_physics.py" "${physics_files[@]}" || true
     ((${#citation_files[@]})) && python3 "${extensionRoot}/resources/scripts/verify_citations.py" "${citation_flags[@]}" "${citation_files[@]}" || true
     ((${#script_files[@]})) && python3 "${extensionRoot}/resources/scripts/check_scripts.py" "${script_files[@]}" || true
   fi
   ```
   Include any other actual reference-list files in citation_files after reading
   them. If a literature task updated `.research/LITERATURE.md`, read it back and
   include it in citation_files too. A nonzero checker exit records findings;
   it never authorizes deletion, edits or an automatic task rejection.
   If any finding is **IMPOSSIBLE** (physics), **NOT_FOUND** / **MISMATCH** (citations), or **WILL NOT RUN** (scripts): show the findings to the researcher and ask via ask_user:
   - header: "Guardrail Findings — Task [NN]"
   - question: "[N] findings:\n\n1. [file:line] [finding] → [suggested fix or closest Crossref match]\n2. ...\n\nHow should I handle them?"
   - options: "Fix them — resume the executor" | "They're fine — note and continue" | "I'll decide per finding"
   Re-dispatch the executor with the accepted fixes when asked, then read all changed files back and rerun the applicable advisory checks before completing. Warnings (IMPLAUSIBLE, UNVERIFIABLE, SUSPECT) are listed in the completion output and noted in the task SUMMARY, not gated.

3. After the researcher has resolved every gated finding and the outputs have been read back, mark task as `☑ complete` in WORKFLOW.md. Update STATE.md: current task = next pending, last completed = [NN].

4. Checkpoint if `auto_checkpoint` is true (default):
   ```bash
   grep -q '"auto_checkpoint": *false' .research/config.json 2>/dev/null || { mkdir -p .research/checkpoints; tar czf ".research/checkpoints/$(date +%Y%m%d-%H%M)-after-task-[NN].tgz" --exclude='./data' --exclude='./checkpoints' -C .research . ; }
   ```

5. Optional git record:
   ```bash
   grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/tasks/task-[NN]/ .research/WORKFLOW.md .research/STATE.md && git commit -m "research(task-[NN]): [task name] — complete"
   ```

**`needs_input: checkpoint:decision` or `needs_input: checkpoint:human-action`:**
- Present what's needed (data, decision, domain knowledge) via ask_user
- Re-dispatch the executor with a `<resume>` block containing the answer (or re-spawn with the full context plus `<resume>`)

**`task_blocked:`:**
- Show blocker clearly
- Offer via ask_user: upload missing data, revise assumptions, execute the blocking task first, or skip this task

**If $ARGUMENTS = "all":** After each task completes, loop to the next pending task. Stop the loop at any needs_input: checkpoint or task_blocked: return and at the first `writing` task.

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

<sub>Each dispatch starts with fresh worker context.</sub>

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
