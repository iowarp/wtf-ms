---
description: "Overview of wtf-MS commands, workflow, and philosophy"
---

<objective>
Display the wtf-MS command reference. No tools needed.
</objective>

<process>

Display the following:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS — Material Science Research System
 Plan and automate your research with Clio Coder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CORE RESEARCH LOOP
─────────────────────────────────────────
 1. /wtfMS:identify-research
       Guided interview → select domain, sub-field,
       scope, and confirm a research prompt

 2. /wtfMS:literature-review
       Review literature, identify gaps, refine keywords
       (loops back to identify-research if needed)

 3. /wtfMS:define-virtual-lab
       Map available resources: experimental equipment,
       HPC systems, software licenses, collaborations
       Questions are targeted to your research domain

 4. /wtfMS:define-research-tasks
       Choose from traditional research workflows or
       build from scratch — interview per task for assumptions
       (resource-aware: flags tasks requiring unavailable equipment)

 5. /wtfMS:execute-task [N | all]
       Execute a specific task or the full workflow
       Types: literature, experimental, computational,
              data-analysis, analytical, writing

 6. /wtfMS:wtfp
       Bridge to wtf-p — translate research into a paper
       project with include/exclude control

TASK MANAGEMENT
─────────────────────────────────────────
 /wtfMS:add-task          Add a task to the workflow
 /wtfMS:remove-task [N]   Remove a task permanently
 /wtfMS:archive-task [N]  Archive (preserve but deactivate)

DATA
─────────────────────────────────────────
 /wtfMS:upload-data [file] Register data files, papers,
                           and datasets for task use

PROGRESS & CONTROL
─────────────────────────────────────────
 /wtfMS:status             Full project dashboard
 /wtfMS:progress           Statusline + smart routing
 /wtfMS:pause-research     Pause + auto-checkpoint
 /wtfMS:resume-research    Resume from paused state
 /wtfMS:checkpoint save [label]   Save state snapshot
 /wtfMS:checkpoint restore [name]  Restore snapshot
 /wtfMS:checkpoint list           List snapshots

META
─────────────────────────────────────────
 /wtfMS:help               This help
 /wtfMS:settings           View/edit project config

PROJECT STATE (.research/)
─────────────────────────────────────────
 RESEARCH.md     Research identity, prompt, scope
 LITERATURE.md   Review results, gaps, keywords
 VIRTUAL-LAB.md  Equipment, HPC, software, gaps
 WORKFLOW.md     Tasks with status and assumptions
 STATE.md        Current position, phase, decisions
 DATA-INDEX.md   Registered data files
 config.json     Settings (web_search, commit_research…)
 data/           Uploaded datasets and papers
 tasks/          Task-by-task outputs (task-NN/)
 checkpoints/    State snapshot archives
 handoff/        Paste-ready blocks for wtf-p 0.6

TASK TYPES
─────────────────────────────────────────
 literature    → Read supplied papers and provided URLs, synthesize
 experimental  → Generate protocol + data templates
 computational → Generate simulation/analysis scripts
 data-analysis → Analyze uploaded data, produce figures
 analytical    → Mathematical modeling, derivations
 writing       → Bridge to /wtfMS:wtfp

GUARDRAILS (after each task, advisory)
─────────────────────────────────────────
 check_physics     impossible values (T < 0 K, ρ ≤ 0…)
 verify_citations  Crossref check on quoted titles/DOIs
 check_scripts     syntax + hallucinated imports
 Findings are shown to you; nothing is auto-removed.

INTEGRATION WITH WTF-P
─────────────────────────────────────────
 /wtfMS:wtfp detects your wtf-p generation.
 0.6+: writes .research/handoff/ blocks you paste into
       /wtfp:new-paper → map-project → create-outline
 0.5:  pre-fills .planning/PROJECT.md directly
 Either way you never re-answer questions already
 answered during research planning.

TIPS
─────────────────────────────────────────
 • Each dispatch receives fresh worker context
 • Interviews happen in the command; agents only
   synthesize and write, and report back checkpoints
 • /wtfMS:upload-data papers BEFORE literature-review:
   supplied papers first, provided URLs second
 • wtf-MS never initializes git. Set commit_research=true in
   /wtfMS:settings if you want commits and tags.
 • /wtfMS:checkpoint save before long tasks
 • /wtfMS:literature-review can loop back to
   identify-research if your prompt needs revision
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

</process>
