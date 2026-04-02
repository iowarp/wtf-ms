---
name: wtfMS:define-research-tasks
description: Build a research workflow — select from traditional templates or create from scratch, with assumption interviews per task
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<execution_context>
@.research/RESEARCH.md
@.research/LITERATURE.md
@.research/VIRTUAL-LAB.md
@.claude/wtf-ms/references/traditional-workflows.md
@.claude/wtf-ms/templates/WORKFLOW.md
</execution_context>

<objective>
Create the research workflow for the project. Either select a traditional workflow template and customize it, or build from scratch. Each task gets assumption interviews. Outputs WORKFLOW.md.

**Orchestrator role:** Load research context, present workflow options, gather customizations via AskUserQuestion, spawn wtfms-workflow-planner agent to generate WORKFLOW.md with assumptions.

**Why subagent:** Workflow decomposition and assumption elicitation require sustained reasoning about research design. Each task's assumptions shape what the executor later needs to do.
</objective>

<context>
No arguments. Requires RESEARCH.md to exist.
</context>

<process>

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

Use AskUserQuestion:
- header: "Research Workflow Design"
- question: "Based on your research (**[research prompt]**), I suggest one of these workflow templates:\n\n**A. [Template name]** — [1-line description, N tasks]\n**B. [Template name]** — [1-line description, N tasks]\n**C. Build from scratch** — I'll define each step\n\nWhich fits best?"
- options: "Template A" | "Template B" | "Template C — Build from scratch" | "Show me all templates"

## 3. Gather Customizations

After template selection, ask about modifications:
Use AskUserQuestion:
- header: "Workflow Customization"
- question: "Template **[selected]** has these tasks:\n\n[numbered list of tasks from template]\n\nWhat changes?\n1. **Add tasks**: Any steps missing for your specific research?\n2. **Remove tasks**: Any steps you'll skip (and why)?\n3. **Reorder**: Any dependencies that differ from the template?"
- options: "Use as-is" | "I have changes" | "Add one task" | "Remove one task"

## 4. Confirm Scope and Exclusions

Use AskUserQuestion:
- header: "Scope & Exclusions"
- question: "Before planning assumptions, confirm:\n1. **Hard constraints**: Which tasks are definitely IN scope?\n2. **Out of scope**: Which standard steps will you skip?\n3. **First milestone**: Which task marks the first major checkpoint?\n4. **Data availability**: Do you have any existing data that eliminates early tasks?"
- options: "Confirmed — proceed to assumptions" | "Let me adjust"

## 5. Spawn wtfms-workflow-planner Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► PLANNING RESEARCH WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Spawn with full context:
```
Task(
  prompt="First, read .claude/agents/wtfMS/workflow-planner.md for your role.\n\n" + filled_prompt,
  subagent_type="general-purpose",
  description="Build Research Workflow"
)
```

Filled prompt includes:
- `<research>` — full RESEARCH.md
- `<literature>` — LITERATURE.md gaps and methods landscape
- `<virtual_lab>` — full VIRTUAL-LAB.md (or "not defined" if missing)
- `<selected_template>` — the chosen template tasks
- `<customizations>` — additions, removals, reorderings
- `<scope_decisions>` — inclusions, exclusions, constraints
- `<workflow_path>` — target: `.research/WORKFLOW.md`

## 6. Handle Agent Return

**`## WORKFLOW COMPLETE`:**
- Create task output directories:
  ```bash
  # Create one directory per task
  for i in $(seq -w 1 [N_TASKS]); do mkdir -p .research/tasks/task-$i; done
  ```
- Update STATE.md (current task = 01, status = planning)
- Commit:
  ```bash
  git add .research/WORKFLOW.md .research/tasks/ .research/STATE.md
  git commit -m "research: workflow defined — [N] tasks, [research type]"
  ```

**`## CHECKPOINT REACHED`:**
- Present assumption question to user, collect domain-expert answer, resume

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

<sub>`/clear` first → fresh context window</sub>

───────────────────────────────────────────

**Task management:**
- `/wtfMS:add-task` — add a task to the workflow
- `/wtfMS:remove-task [N]` — remove a task
- `/wtfMS:archive-task [N]` — archive without deleting

</offer_next>

<success_criteria>
- [ ] Traditional workflow template presented as starting point
- [ ] User customizations captured (add/remove/reorder)
- [ ] Scope and exclusions explicitly confirmed
- [ ] Each task has: type, description, assumptions, inputs, outputs, dependencies
- [ ] Tasks are specific and actionable (not vague like "do experiment")
- [ ] Task directories created under .research/tasks/
- [ ] WORKFLOW.md committed
</success_criteria>
