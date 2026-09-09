---
name: wtfMS:help
description: Overview of wtf-MS commands, workflow, and philosophy
allowed-tools: []
---

<objective>
Display the wtf-MS command reference. No tools needed.
</objective>

<process>

Display the following:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS — Material Science Research System
 Plan and automate your research with Claude
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
 /wtfMS:cost               Token usage + est. cost per step
 /wtfMS:pause-research     Pause + auto-checkpoint
 /wtfMS:resume-research    Resume from paused state
 /wtfMS:checkpoint save [label]   Save state snapshot
 /wtfMS:checkpoint restore [tag]  Restore snapshot
 /wtfMS:checkpoint list           List snapshots

META
─────────────────────────────────────────
 /wtfMS:help               This help
 /wtfMS:settings           View/edit project config

PROJECT STATE (.research/)
─────────────────────────────────────────
 RESEARCH.md     Research identity, prompt, scope
 LITERATURE.md   Review results, gaps, keywords
 WORKFLOW.md     Tasks with status and assumptions
 STATE.md        Current position, phase, decisions
 DATA-INDEX.md   Registered data files
 data/           Uploaded datasets and papers
 tasks/          Task-by-task outputs

TASK TYPES
─────────────────────────────────────────
 literature    → Search, read, synthesize papers
 experimental  → Generate protocol + data templates
 computational → Generate simulation/analysis scripts
 data-analysis → Analyze uploaded data, produce figures
 analytical    → Mathematical modeling, derivations
 writing       → Bridge to /wtfMS:wtfp

INTEGRATION WITH WTF-P
─────────────────────────────────────────
 /wtfMS:wtfp pre-fills .planning/PROJECT.md so you
 never re-answer questions already answered during
 research planning. Your research context flows
 directly into paper writing.

TIPS
─────────────────────────────────────────
 • /clear before each command → peak agent quality
 • /wtfMS:checkpoint save before long tasks
 • /wtfMS:upload-data before execute-task for data tasks
 • /wtfMS:literature-review can loop back to
   identify-research if your prompt needs revision
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

</process>
