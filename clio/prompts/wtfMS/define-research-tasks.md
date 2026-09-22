---
description: "Build a research workflow — select from traditional templates or create from scratch, with assumption interviews per task"
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
@.research/RESEARCH.md
@.research/LITERATURE.md
@.research/VIRTUAL-LAB.md
@${extensionRoot}/resources/references/traditional-workflows.md
@${extensionRoot}/resources/templates/WORKFLOW.md
</execution_context>

<objective>
Create the research workflow for the project. Either select a traditional workflow template and customize it, or build from scratch. Each task gets an assumption interview. Outputs WORKFLOW.md.

**Orchestrator role:** Load research context, present workflow options, gather customizations and scope, run the per-task assumption interview, spawn the wtfms-workflow-planner agent to generate WORKFLOW.md, present resource flags and planner defaults for decision, re-dispatch the agent with revisions, create task directories, record.

**Why the interview lives here:** Subagents cannot prompt the user on any host. Assumptions are research decisions and only the researcher can make them, so this command collects them before the planner runs. The planner gets a fresh context for the reasoning that benefits from it: feasibility against VIRTUAL-LAB.md, dependency ordering, and writing a WORKFLOW.md the executor can run without interpretation.
</objective>

<context>
No arguments. Requires RESEARCH.md to exist.
</context>

<process>

Worker write scope: .research/WORKFLOW.md.


## 1. Validate Environment

```bash
[ ! -f .research/RESEARCH.md ] && echo "ERROR: No RESEARCH.md. Run /wtfMS:identify-research first." && exit 1
[ -f .research/WORKFLOW.md ] && echo "WARN: WORKFLOW.md exists — running again will replace it."
cat .research/RESEARCH.md
[ -f .research/LITERATURE.md ] && cat .research/LITERATURE.md | head -60
```

Check for VIRTUAL-LAB.md and warn if missing:
```bash
if [ ! -f .research/VIRTUAL-LAB.md ]; then
  echo "NOTE: No VIRTUAL-LAB.md found. Run /wtfMS:define-virtual-lab to map your resources first."
  echo "Proceeding without resource constraints — tasks may be planned that require unavailable equipment."
fi
[ -f .research/VIRTUAL-LAB.md ] && cat .research/VIRTUAL-LAB.md
```

## 2. Present Workflow Template Options

Based on the research type from RESEARCH.md (experimental / computational / mixed / literature-only), present the relevant traditional workflow templates from traditional-workflows.md.

Use ask_user:
- header: "Research Workflow Design"
- question: "Based on your research (**[research prompt]**), I suggest one of these workflow templates:\n\n**A. [Template name]** — [1-line description, N tasks]\n**B. [Template name]** — [1-line description, N tasks]\n**C. Build from scratch** — I'll define each step\n\nWhich fits best?"
- options: "Template A" | "Template B" | "Template C — Build from scratch" | "Show me all templates"

## 3. Gather Customizations

After template selection, ask about modifications:
Use ask_user:
- header: "Workflow Customization"
- question: "Template **[selected]** has these tasks:\n\n[numbered list of tasks from template]\n\nWhat changes?\n1. **Add tasks**: Any steps missing for your specific research?\n2. **Remove tasks**: Any steps you'll skip (and why)?\n3. **Reorder**: Any dependencies that differ from the template?"
- options: "Use as-is" | "I have changes" | "Add one task" | "Remove one task"

## 4. Confirm Scope and Exclusions

Use ask_user:
- header: "Scope & Exclusions"
- question: "Before planning assumptions, confirm:\n1. **Hard constraints**: Which tasks are definitely IN scope?\n2. **Out of scope**: Which standard steps will you skip?\n3. **First milestone**: Which task marks the first major checkpoint?\n4. **Data availability**: Do you have any existing data that eliminates early tasks?"
- options: "Confirmed — proceed to assumptions" | "Let me adjust"

## 5. Assumption Interview, Per Task

You now hold the final task list. For each task, ask the question block for its type. Batch tasks of the same type into one ask_user when there are three or fewer; otherwise one question per task. Use the "Key assumptions to interview about" hints in traditional-workflows.md for the selected template to sharpen the prompts. Every question offers "Use planner defaults for this task" so the researcher can skip and confirm later.

**For experimental tasks:**
- header: "Assumptions: Task [NN] — [name]"
- question: "For '[task description]', I need to understand your assumptions:\n1. **Sample preparation**: What processing route? What contamination risks?\n2. **Characterization**: Which tools are available? What resolution/sensitivity?\n3. **Test conditions**: Temperature, strain rate, environment, standards (ASTM/ISO)?\n4. **Sample size/replicates**: How many samples? What's statistically sufficient?\n5. **Success criteria**: What result would confirm or disprove your hypothesis?"
- options: "Provided details" | "Use planner defaults for this task"

**For computational tasks:**
- header: "Assumptions: Task [NN] — [name]"
- question: "For '[task description]':\n1. **Method**: DFT, MD, phase-field, CALPHAD — which and why?\n2. **Software**: VASP, LAMMPS, Thermo-Calc, etc.?\n3. **Functional/force field**: Exchange-correlation functional or interatomic potential?\n4. **System size and timescale**: Feasible with available resources?\n5. **Validation benchmark**: What experimental data exists to validate against?"
- options: "Provided details" | "Use planner defaults for this task"

**For data-analysis tasks:**
- header: "Assumptions: Task [NN] — [name]"
- question: "For '[task description]':\n1. **Data source**: Which uploaded files? Which task outputs?\n2. **Statistical approach**: What statistical tests are appropriate?\n3. **Outlier handling**: Expected outliers? How to treat them?\n4. **Visualization**: What plots are needed for the paper?\n5. **Software**: Python/MATLAB/R? Which libraries?"
- options: "Provided details" | "Use planner defaults for this task"

**For literature tasks:**
- header: "Assumptions: Task [NN] — [name]"
- question: "For '[task description]':\n1. **Scope**: Which sub-topics to cover?\n2. **Inclusion criteria**: Year range, journal type, minimum citation count?\n3. **Key authors/groups**: Anyone to prioritize?\n4. **Output format**: Structured table? Narrative summary? BibTeX file?"
- options: "Provided details" | "Use planner defaults for this task"

**For analytical tasks:**
- header: "Assumptions: Task [NN] — [name]"
- question: "For '[task description]':\n1. **Governing model**: Which physical model or theory?\n2. **Boundary conditions and simplifications**: What is held fixed or neglected?\n3. **Validation**: Which limiting cases or data will the model be checked against?\n4. **Implementation**: Analytical only, or numerical (Python/MATLAB)?"
- options: "Provided details" | "Use planner defaults for this task"

Writing tasks need no interview; they bridge to `/wtfMS:wtfp`.

Collect every answer verbatim into `<assumptions>`, keyed by task name, with "planner defaults requested" where the researcher skipped.

## 6. Spawn wtfms-workflow-planner Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► PLANNING RESEARCH WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use dispatch with `agent: "wtfms-workflow-planner"` and a task containing the assignment and full context. The prompt carries:
- `<research>` — full RESEARCH.md
- `<literature>` — LITERATURE.md gaps and methods landscape
- `<virtual_lab>` — full VIRTUAL-LAB.md (or "not defined" if missing)
- `<selected_template>` — the chosen template tasks
- `<customizations>` — additions, removals, reorderings
- `<scope_decisions>` — inclusions, exclusions, first milestone, existing data
- `<assumptions>` — the per-task answers from Step 5
- `<workflow_path>` — `.research/WORKFLOW.md`

## 7. Decide on Flags and Defaults

**`workflow_complete:`:**

```bash
test -s .research/WORKFLOW.md && echo OK || echo "ERROR: WORKFLOW.md missing"
grep -c "^### Task" .research/WORKFLOW.md
```
If missing, re-dispatch the agent and say so.

Present the planner's return and ask via ask_user, one turn:
- header: "Workflow Review"
- question: "[N] tasks planned. Critical path: [A → B → C]. First checkpoint after Task [NN].\n\n**Resource flags** ([N]):\n- ⚠ Task [NN]: [gap] → applied: [alternative]\n- BLOCKED Task [NN]: [gap] → proposed: [remove/replace]\n\n**Planner defaults to confirm** ([N]):\n- Task [NN]: [assumption]\n\nDoes this order make sense? Decide on each flag and default, or accept as written."
- options: "Accept as written" | "I have decisions on the flags" | "Confirm defaults with edits" | "Change the task order"

If anything changes: re-dispatch the planner with a `<revisions>` block (or re-spawn with the full context plus `<revisions>`), then re-verify the file.

**`needs_input: checkpoint:decision` or `needs_input: checkpoint:human-action`:** Present the question via ask_user, collect the domain-expert answer, re-dispatch the agent.

## 8. Create Task Directories and State

```bash
N=$(grep -c "^### Task" .research/WORKFLOW.md)
for i in $(seq 1 "$N"); do mkdir -p ".research/tasks/task-$(printf '%02d' "$i")"; done
ls .research/tasks/
```

Update STATE.md: current phase = executing, current task = 01, status = planning. Keep the Decisions Made list and append the workflow decisions.

Optional git record:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/WORKFLOW.md .research/tasks/ .research/STATE.md && git commit -m "research: workflow defined — [N] tasks, [research type]"
```

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► WORKFLOW DEFINED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workflow: .research/WORKFLOW.md
Tasks:    [N] tasks ([type])

| # | Task | Type | Depends On |
|---|------|------|------------|
[table from WORKFLOW.md]

───────────────────────────────────────────

## ▶ Next Up

**Execute the first task**

`/wtfMS:execute-task 1`

<sub>Each dispatch starts with fresh worker context.</sub>

───────────────────────────────────────────

**Task management:**
- `/wtfMS:add-task` — add a task to the workflow
- `/wtfMS:remove-task [N]` — remove a task
- `/wtfMS:archive-task [N]` — archive without deleting

</offer_next>

<success_criteria>
- [ ] Every question to the researcher was asked by this command, not by the agent
- [ ] Traditional workflow template presented as starting point
- [ ] User customizations captured (add/remove/reorder)
- [ ] Scope and exclusions explicitly confirmed
- [ ] Assumption interview run per task before planning; skips recorded as planner defaults
- [ ] Resource flags and planner defaults decided by the researcher
- [ ] Each task has: type, description, assumptions, inputs, outputs, dependencies
- [ ] Task directories created with two-digit numbering for every task count
- [ ] WORKFLOW.md verified on disk; commit only if commit_research is true
</success_criteria>
