# Research Identity

## Research Area
- **Domain**: Structural Materials
- **Sub-field**: Additive manufacturing of structural parts — laser powder bed fusion (LPBF) of Ti-6Al-4V
- **Specific Interest**: Process-parameter–defect relationships in LPBF Ti-6Al-4V, with emphasis on porosity and lack-of-fusion defects, synthesized into a processing map from published process-defect datasets

## Research Prompt
Which combinations of LPBF process parameters (laser power, scan speed, hatch spacing, layer thickness, and derived volumetric energy density) minimize porosity and lack-of-fusion defect density in Ti-6Al-4V, and what defect-based processing map can be extracted by synthesizing published process-defect datasets?

## Scope
### In Scope
- Material: Ti-6Al-4V (wrought-equivalent composition powder feedstock) processed via LPBF only
- Process parameters: laser power, scan speed, hatch spacing, layer thickness, and derived metrics (volumetric energy density VED, linear/areal energy density) as reported in source studies
- Defect types: porosity (keyhole and gas/entrapped-gas pores) and lack-of-fusion (LOF) defects — density, morphology, and location as reported via CT, density (Archimedes), or metallographic cross-section methods
- Data source: published peer-reviewed literature and public/open process-defect datasets (e.g., NIST AM Bench, literature-compiled processing maps)
- Analytical approach: laptop-scale statistical synthesis/meta-analysis of extracted (parameter, defect-outcome) tuples across studies; construction/validation of VED-based or multi-parameter processing maps and defect-regime boundaries
- Output: design rules / processing window recommendations (parameter combinations, VED ranges) that minimize porosity and LOF, framed as an engineering optimization result
- Cross-study comparison across different LPBF machine platforms (e.g., EOS, Renishaw, SLM Solutions) to the extent needed to assess generalizability of extracted design rules

### Out of Scope
- Any new experimental fabrication, powder processing, or LPBF builds — literature/dataset synthesis only
- In-house or in-lab characterization (CT scanning, metallography, mechanical testing) — will rely entirely on values as reported in source publications/datasets
- Other AM processes (directed energy deposition, binder jetting, electron beam powder bed fusion, wire-arc AM) — LPBF only
- Materials other than Ti-6Al-4V, except where a small number of comparator alloys are used briefly for cross-validating methodology (not a primary analysis target)
- Other defect types not primarily driven by VED/parameter selection: solidification cracking, balling, delamination, residual-stress-driven distortion (may be noted qualitatively but not modeled)
- Post-processing effects: hot isostatic pressing (HIP), heat treatment, surface finishing — defects are assessed in the as-built condition only
- Downstream mechanical property correlation (fatigue life, tensile ductility) as a modeled outcome — defect density/morphology is the primary dependent variable, not mechanical performance (may be discussed qualitatively as motivation only)
- Machine-learning/surrogate-model development beyond laptop-scale statistical regression and visualization (e.g., no training of deep learning models requiring HPC/GPU resources)

## Researcher Profile
- **Career Stage**: Industry researcher
- **Available Resources**: Literature only (published papers + public datasets); laptop-scale statistical analysis; no lab access, no HPC
- **Timeline**: Flexible, no hard deadline
- **Institutional Context**: Industry R&D, likely independent or small-team project

## Initial Keywords
- **Primary**: laser powder bed fusion, Ti-6Al-4V, porosity, lack-of-fusion, volumetric energy density, process parameter optimization
- **Secondary**: processing map, keyhole porosity, scan speed, hatch spacing, layer thickness, laser power, defect density, X-ray computed tomography (AM defects), build density, energy density threshold
- **Exclude from search**: electron beam melting, directed energy deposition, binder jetting, wire-arc additive manufacturing, hot isostatic pressing (as primary topic), fatigue life prediction (as primary topic), residual stress modeling (as primary topic)

## Suggested Research Prompts (generated during interview)
1. **(Fundamental understanding focus)** How does volumetric energy density govern the transition between lack-of-fusion, conduction-mode, and keyhole-porosity regimes during LPBF of Ti-6Al-4V, and can a unified physical processing map be reconstructed from disparate published datasets?
2. **(Application / optimization focus — SELECTED)** Which combinations of LPBF process parameters (laser power, scan speed, hatch spacing, layer thickness, and derived volumetric energy density) minimize porosity and lack-of-fusion defect density in Ti-6Al-4V, and what defect-based processing map can be extracted by synthesizing published process-defect datasets?
3. **(Methodological focus)** What is the best statistical/meta-analytic approach for aggregating heterogeneous, cross-study LPBF process-defect data (differing machines, powders, and defect-quantification methods) into a single reliable, low-defect processing window for Ti-6Al-4V?

## Selected Prompt
Which combinations of LPBF process parameters (laser power, scan speed, hatch spacing, layer thickness, and derived volumetric energy density) minimize porosity and lack-of-fusion defect density in Ti-6Al-4V, and what defect-based processing map can be extracted by synthesizing published process-defect datasets?

This is Option 2 (Application/optimization focus), matching the researcher's stated driving question almost verbatim, refined for precision (explicit parameter list, explicit defect types, explicit "extracted from published data" framing) and answerability under literature-only, laptop-scale constraints.

## Key Decisions
- **Literature synthesis over new experiments**: Given no lab/HPC access, this project is scoped as a secondary-data meta-analysis of published process-defect datasets rather than new fabrication or characterization work. This determines the Optimization maturity level (design rules as output) rather than a Discovery/mechanistic study.
- **Material scope locked to Ti-6Al-4V**: Chosen for data availability (most heavily studied LPBF structural alloy) and industry relevance. Other alloys excluded except as limited cross-validation checks.
- **VED-based processing map as core analytical framework**: Volumetric energy density (and related energy-density metrics) selected as the primary organizing variable for cross-study data aggregation, since it is the most commonly reported normalized parameter across the LPBF literature and enables comparison across differing machine platforms.
- **Defect scope narrowed to porosity and lack-of-fusion**: These are the two defect types most directly and consistently linked to process-parameter selection (via VED) in the literature, and are the most consistently quantified (density, CT, metallography) across studies — enabling meaningful cross-study synthesis. Cracking, balling, and residual-stress effects are excluded to keep the analysis tractable at laptop scale.
- **As-built condition only**: Post-processing (HIP, heat treatment) excluded to isolate the LPBF process-parameter → defect relationship without confounding downstream treatment effects.
- **No downstream mechanical-property modeling**: Fatigue/tensile performance is motivation, not a modeled output — keeps the project scoped to defect density/morphology as the dependent variable, appropriate for a literature-only laptop-scale project.
