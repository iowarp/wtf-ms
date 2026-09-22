---
name: wtfms-workflow-planner
description: "Build a resource-aware dependency plan with researcher assumptions and tagged defaults."
---

Load the linked references when their domain or template is needed. Resolve
them from this skill directory; their contents are copied verbatim from Daisy's
canonical research resources. Researcher questions belong to the orchestrator.

- [traditional-workflows.md](references/traditional-workflows.md)
- [WORKFLOW.md](references/WORKFLOW.md)
- [VIRTUAL-LAB.md](references/VIRTUAL-LAB.md)
- [RESEARCH.md](references/RESEARCH.md)

## Plans Are Prompts

WORKFLOW.md is not a project management document. It IS the executable specification. Each task entry must contain everything the task-executor needs to run it without interpretation — specific inputs, expected outputs, and documented assumptions.

## Assumptions Are Research Decisions

Every assumption in a research workflow is a scientific decision. "We assume linear elastic behavior" is not just a simplification — it's a testable claim that could be wrong and should be documented. Good assumptions are:
- **Explicit**: Written down, not implied
- **Justified**: Why this assumption is reasonable
- **Testable**: How you'd know if the assumption breaks

Assumptions the researcher stated in the interview are theirs; record them verbatim with `[researcher]`. Assumptions you supplied are defaults; mark them `[planner default — confirm]`.

## Task Atomicity

Each task should be completable in one focused work session (hours to days, not weeks). If a task is too large, split it. Signs of an oversized task:
- Multiple distinct outputs
- Multiple methods applied
- Results from one part needed before another part can proceed

## Traditional Workflows as Starting Points

Traditional workflows encode decades of research practice. They are starting points, not constraints. Honor the researcher's customizations and document why standard steps were modified or skipped.



If VIRTUAL-LAB.md is provided, check every task against its Resource-to-Task Mapping table:
- Required resource available → feasible
- Required resource has a gap → flag with ⚠ and the alternative from VIRTUAL-LAB.md
- Required resource completely unavailable with no alternative → mark `BLOCKED` and propose removing or replacing the task

Example flags:
- "⚠ Task 05 (TEM characterization): No in-house TEM. External facility available (2–3 week lead time) — add booking step."
- "⚠ Task 07 (DFT with VASP): No VASP license. Alternative: Quantum ESPRESSO (free, installed on HPC)."

Every flag goes into the return block for the researcher's decision. Apply the alternative provisionally so the workflow is complete either way.

If VIRTUAL-LAB.md is missing, note in Workflow Decisions that feasibility was not checked.

## Step 5: Attach Assumptions

For each task, write the assumptions from `<assumptions>` verbatim, tagged `[researcher]`. Cover, per type, at least:

- **experimental**: sample preparation route and contamination risks; characterization tools and resolution; test conditions and standards (ASTM/ISO); sample size and replicates; success criteria
- **computational**: method and why; software; functional or force field; system size and timescale vs available resources; validation benchmark
- **data-analysis**: data source; statistical approach; outlier handling; visualizations needed; software and libraries
- **literature**: sub-topic scope; inclusion criteria; priority authors; output format
- **analytical**: governing model; boundary conditions; validation limit cases

Where the interview left a slot empty, supply a defensible default tagged `[planner default — confirm]` and add it to the return block.


