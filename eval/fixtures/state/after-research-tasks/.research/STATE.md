# Research State

## Current Phase
workflow-defined → executing (current task: 01, status: planning)

## Research Prompt
Which combinations of LPBF process parameters (laser power, scan speed, hatch spacing, layer thickness, and derived volumetric energy density) minimize porosity and lack-of-fusion defect density in Ti-6Al-4V, and what defect-based processing map can be extracted by synthesizing published process-defect datasets?

## Decisions Made
- Domain: Structural Materials — Additive manufacturing of structural parts (LPBF of Ti-6Al-4V)
- Selected prompt: Option 2 (Application/optimization focus) — matches researcher's driving question, sharpened for precision (explicit parameter list, explicit defect types) and answerability given literature-only, laptop-scale resources
- Scope boundary: Ti-6Al-4V only, LPBF only, porosity + lack-of-fusion defects only, as-built condition (no HIP/heat treatment), literature/dataset synthesis only (no new fabrication or in-lab characterization), VED-based processing map as the core analytical framework
- Literature review complete (LITERATURE.md) — confirmed prompt is well-positioned; core gaps are (1) no cross-study/cross-platform Ti-6Al-4V processing map exists, (2) VED's non-uniqueness is unvalidated on a multi-source Ti-6Al-4V dataset
- Virtual lab defined (VIRTUAL-LAB.md) — literature-only, laptop-scale Python (pandas/numpy/scipy/matplotlib) stack, no lab/HPC/commercial software
- Workflow defined from scratch (WORKFLOW.md) — 4 sequential tasks: (01) extract process-defect datapoints, (02) compile/clean unified dataset, (03) statistical analysis + VED processing map, (04) synthesize findings/limitations

## Open Questions
- Whether cross-machine-platform generalizability of a single VED-based processing map is defensible, or whether machine-specific sub-maps will be needed (to be tested via leave-one-study-out CV in Task 03)
- Whether the ≥8 studies / ≥80 datapoints heuristic target (set as an autonomous-mode assumption in WORKFLOW.md) will actually be achievable during Task 01 extraction
- Whether Zenodo/PMC/NIST candidate datasets identified in literature review will prove directly usable or require significant reconciliation with manually-extracted literature tuples

## Last Updated
2026-07-23T00:00:00Z
