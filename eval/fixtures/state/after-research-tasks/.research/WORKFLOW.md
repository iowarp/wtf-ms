# Research Workflow

## Research Type
literature-only

## Overview
This is a secondary-data meta-analysis: published LPBF Ti-6Al-4V process-defect datapoints are extracted from the literature, compiled into a single cleaned dataset, statistically analyzed to build and stress-test a VED-based (and multi-parameter) defect processing map, and synthesized into design-rule findings with explicit limitations. No new experiments, characterization, or ML/HPC modeling are performed — every task runs on a laptop with Python (pandas/numpy/scipy/matplotlib) plus manual/PDF-assisted literature extraction.

## Tasks

### Task 01: Extract process-defect datapoints from published LPBF Ti-6Al-4V literature
- **Type**: literature
- **Description**: Systematically extract (laser power P, scan speed v, hatch spacing h, layer thickness t, reported/derived VED, porosity %, LOF density/presence, pore morphology/location where available, machine platform, measurement method) tuples from peer-reviewed papers and public datasets. Start from the candidate sources already identified in LITERATURE.md (Zenodo LPBF Ti-6Al-4V dataset, companion PMC dataset, NIST AM-Bench if relevant) and expand via targeted search for additional independent studies until the minimum independent-study threshold (see assumptions) is met or literature saturation is reached (new searches return no new usable datapoints).
- **Assumptions**:
  - **Minimum corpus size**: at least 8 independent studies/datasets (not counting sub-tables from the same source as separate studies) and at least 80 total (P,v,h,t,defect) datapoints are needed for the statistical synthesis in Task 03 to be meaningful (enough degrees of freedom for regression across 4+ parameters plus machine-platform grouping). This is a heuristic, not a formal power calculation — justified by rule-of-thumb ≥10 datapoints per predictor for exploratory regression (4 core parameters + 1 platform factor ≈ 5 predictors → ≥50 minimum, rounded up to 80 for safety margin given expected noise/heterogeneity). If saturation is reached below this count, proceed but flag the shortfall explicitly in Task 04 limitations.
  - **Inclusion criteria**: peer-reviewed journal articles, conference papers with sufficient methodological detail, and vetted open datasets (Zenodo/PMC/NIST) published from 2010 onward (LPBF Ti-6Al-4V literature is sparse before this). No citation-count minimum is imposed (field is young; useful data may be in lower-cited papers) but conference abstracts without a methods section are excluded.
  - **Only as-built condition** data is extracted; any datapoint description that is ambiguous about HIP/heat-treatment status is excluded rather than assumed as-built.
  - **PDF-table extraction tooling** (camelot/pdfplumber) is used opportunistically where installed and effective; manual transcription into the tracking spreadsheet is the fallback for figures, scanned tables, or tools that fail to parse cleanly. Every manually transcribed value is spot-checked once against the source.
  - **Bibliography tracking** is manual (spreadsheet/markdown table), since no reference manager is confirmed installed.
  - **Rubenchik et al. dimensionless-scaling citation** (flagged as bibliographically unverified in LITERATURE.md) is excluded from Task 01 extraction unless independently re-verified; if used later it is cited with a caveat.
- **Inputs**: RESEARCH.md, LITERATURE.md (candidate source list and gap analysis), researcher's institutional/personal journal access, public internet access to Zenodo/PMC/NIST AM-Bench.
- **Expected Outputs**:
  - `data/raw_extraction_log.csv` — one row per (study, parameter-set) datapoint with all fields above plus source citation key and extraction method (dataset-download vs. manual-transcription vs. PDF-table-parse).
  - `data/bibliography.md` — running list of all included sources with full citation, access date, and one-line note on what was extracted from each.
  - A short extraction-log note documenting any papers excluded and why (screened-out list), to support later reproducibility.
- **Dependencies**: none
- **Estimated Effort**: 2-3 weeks (part-time, single researcher; bulk of workflow effort is here)
- **Status**: ☐ pending
- **Notes**: []

---

### Task 02: Compile and clean into one unified analysis dataset
- **Type**: data-analysis
- **Description**: Merge all per-source extraction outputs from Task 01 into a single unified, analysis-ready tabular dataset with consistent units, consistent VED definitions, harmonized machine-platform labels, and documented handling of missing/heterogeneous fields. Compute derived quantities (VED, linear energy density, areal energy density) uniformly from raw P/v/h/t where the source did not already report them, using a single documented formula so all rows are comparable.
- **Assumptions**:
  - **VED formula**: use volumetric energy density = P / (v × h × t) as the single unifying definition across all sources; where a source reports a different VED formula (e.g., omitting hatch spacing, or using absorptivity-corrected energy density), recompute from raw P/v/h/t rather than trusting the source's own VED value, and keep the source-reported VED as a separate column for transparency/cross-check.
  - **Heterogeneous measurement-method handling**: porosity/defect values are tagged by measurement method (XCT, Archimedes density, optical metallography) as a categorical column rather than pooled as equivalent — Archimedes gives bulk density only (no defect type/location per LITERATURE.md), so Archimedes-only rows are flagged and excluded from any analysis requiring defect-type discrimination (Task 03), while still usable for density-only trend checks.
  - **Cross-machine-platform heterogeneity**: machine platform (EOS, Renishaw, SLM Solutions, other/unspecified) is retained as an explicit categorical variable rather than pooled anonymously, enabling Task 03 to test platform as a covariate/grouping factor rather than assuming a single universal map applies.
  - **Missing-data handling**: rows missing any of the 4 core process parameters (P, v, h, t) are excluded from the unified dataset (cannot compute VED); rows missing only defect morphology/location (but with a valid porosity % or LOF presence/absence) are retained with morphology fields left null, since Task 03's primary analysis is on defect density not morphology (per Gap 4 in LITERATURE.md, morphology synthesis is a stretch goal, not the core deliverable).
  - **Outlier/duplicate handling**: exact duplicate parameter-sets from the same source are collapsed to one row (averaged if replicate values differ); cross-source duplicate parameter combinations are retained as separate rows (different studies, informative for reproducibility assessment) but flagged with a `possible_duplicate_of` note.
  - **Units**: standardize to SI-derived engineering units used across the field (P in W, v in mm/s, h and t in mm or µm as commonly reported — pick µm for h/t, mm/s for v — VED in J/mm³) with one documented conversion table.
- **Inputs**: `data/raw_extraction_log.csv` and `data/bibliography.md` from Task 01.
- **Expected Outputs**:
  - `data/unified_dataset.csv` — the single clean analysis dataset, one row per parameter-set-defect-observation, with all harmonized/derived fields and method/platform flags.
  - `data/data_dictionary.md` — column definitions, units, VED formula used, and a log of every exclusion/collapsing decision made during cleaning (for reproducibility).
- **Dependencies**: Task 01
- **Estimated Effort**: 3-5 days
- **Status**: ☐ pending
- **Notes**: []

---

### Task 03: Statistical analysis + build the VED-based defect processing map
- **Type**: data-analysis
- **Description**: Using `data/unified_dataset.csv`, (a) reproduce the standard scalar-VED processing map (VED vs. porosity/LOF, colored by defect regime: dense/LOF/keyhole/balling) and quantify its predictive scatter/non-uniqueness (testing Gap 2 — whether same-VED points diverge in outcome); (b) fit and compare a multi-parameter statistical model (e.g., multiple linear/logistic regression or classification on P, v, h, t individually, plus machine-platform as a factor) against the scalar-VED-only model, using standard goodness-of-fit/classification metrics; (c) test whether machine-platform is a significant covariate (i.e., whether a single cross-platform map is defensible or platform-specific sub-maps are needed); (d) produce a final recommended processing window (parameter/VED ranges) that minimizes porosity and LOF, with explicit confidence bounds given the underlying data scatter.
- **Assumptions**:
  - **Statistical methods**: multiple linear regression (continuous porosity %) and/or multinomial logistic regression (categorical defect regime: dense/LOF/keyhole/balling) fit via `scipy`/basic `numpy` least-squares or a simple closed-form logistic fit — no ML/HPC surrogate modeling, consistent with VIRTUAL-LAB.md constraints. Model comparison uses R²/adjusted-R² (regression) or classification accuracy/confusion matrix (regime classification), plus a likelihood-ratio or F-test comparing scalar-VED-only vs. multi-parameter model.
  - **"Validated processing map" success criterion**: a map is considered validated for this project if (i) it correctly classifies the defect regime for at least ~80% of held-out datapoints (simple train/test split or leave-one-study-out cross-validation, given the whole-study heterogeneity concern), and (ii) the multi-parameter model shows statistically significant improvement (p < 0.05) over scalar-VED alone, OR scalar-VED is shown to be adequate (no significant improvement) — either outcome is a valid, reportable result for Gap 2. There is no external published benchmark to validate against (per LITERATURE.md, no existing cross-study quantification exists), so validation is internal (leave-one-study-out) rather than against a prior gold-standard map.
  - **Cross-validation scheme**: leave-one-study-out (not random k-fold) is used as the primary validation method, since random splitting could leak study-specific systematic bias (e.g., machine calibration) into both train and test sets and overstate generalizability — this directly tests cross-study/cross-platform generalizability, which is the paper's core claim.
  - **Layer-thickness/high-productivity regime (100-250 µm, Gap 3)**: analyzed as a separate stratified subset if ≥10 datapoints exist in that range; otherwise explicitly noted as data-sparse and excluded from the primary processing map with a call-out in Task 04 limitations rather than extrapolated into.
  - **Handling of non-unique VED outcomes**: points with near-identical VED (within a small tolerance, e.g., ±5%) but differing defect regimes are explicitly tabulated as a "VED non-uniqueness" sub-analysis, directly addressing Gap 2.
- **Inputs**: `data/unified_dataset.csv`, `data/data_dictionary.md` from Task 02.
- **Expected Outputs**:
  - `analysis/ved_processing_map.png` — scalar-VED processing map (VED vs. porosity, colored/marked by regime and machine platform).
  - `analysis/multiparameter_model_results.md` — regression/classification model outputs, comparison metrics, and significance tests (scalar-VED vs. multi-parameter vs. platform-as-covariate).
  - `analysis/recommended_processing_window.md` — final parameter/VED range recommendations with confidence bounds and the regime/platform caveats under which they hold.
  - `analysis/ved_nonuniqueness_table.csv` — tabulated near-identical-VED, divergent-outcome datapoints (Gap 2 evidence).
  - Analysis script(s) (`analysis/build_processing_map.py` or equivalent) used to generate the above, so the analysis is reproducible.
- **Dependencies**: Task 02
- **Estimated Effort**: 1-2 weeks
- **Status**: ☐ pending
- **Notes**: []

---

### Task 04: Synthesize findings and limitations
- **Type**: writing
- **Description**: Write the final synthesis document integrating Task 01-03 outputs into a coherent narrative: state the design-rule/processing-window recommendation, the evidence for/against scalar VED's adequacy, the cross-platform generalizability finding, and a full limitations section covering data heterogeneity, corpus size, measurement-method mixing, and any scope items intentionally excluded (mechanical-property correlation, HIP/heat-treatment, non-VED-driven defect types).
- **Assumptions**:
  - **Output format**: a single structured markdown report (`synthesis/FINDINGS.md`) containing: (1) executive summary of the recommended processing window, (2) methodology summary (corpus size, inclusion criteria, cleaning decisions — pointers back to Tasks 01-02 artifacts), (3) results (processing map figure, model comparison, non-uniqueness evidence, platform-covariate finding), (4) limitations (explicit, itemized), (5) suggested future work (e.g., what a follow-up in-house validation experiment could test, even though out of scope here). This format is chosen because it maps directly onto a future manuscript structure (compatible with a later `/wtfMS:wtfp` bridge to a paper project) while remaining a standalone deliverable if publication is not pursued.
  - **Limitations section is mandatory and specific**, not boilerplate — must explicitly restate: corpus size actually achieved vs. the ≥8-study/≥80-datapoint target from Task 01, the fraction of data excluded for missing fields, the Archimedes-vs-XCT measurement-method mixing caveat, the fact that no external benchmark existed for validating the meta-analysis methodology itself (novel-methodology caveat per LITERATURE.md), and the 316L/IN718-vs-Ti-6Al-4V methodological-transfer caveat for any VED-critique literature leaned on.
  - **No new claims beyond what Tasks 01-03 support**: findings are strictly a synthesis of the extracted/analyzed data — no new modeling, no mechanical-property inference, no HIP/heat-treatment extrapolation.
- **Inputs**: `data/unified_dataset.csv`, `data/data_dictionary.md`, all `analysis/*` outputs from Task 03, `data/bibliography.md`.
- **Expected Outputs**:
  - `synthesis/FINDINGS.md` — the full synthesis report as described above.
  - `synthesis/limitations_checklist.md` — the itemized limitations list, kept as a standalone artifact for easy reuse if this project is later bridged into a paper draft.
- **Dependencies**: Task 03
- **Estimated Effort**: 3-5 days
- **Status**: ☐ pending
- **Notes**: []

---

## Archived Tasks
[none]

## Workflow Decisions

- **Built from scratch, not a traditional template**: this is a pure literature-synthesis/meta-analysis project with no experimental or computational-simulation component, so no standard experimental/computational workflow template applied. The user-specified 4-task skeleton (extract → compile/clean → analyze/map → synthesize) was used as-is; each task was fleshed out but the count was deliberately kept at 4 per explicit user instruction, since each stage is already a natural, non-splittable unit of work (single dominant output per task: extraction log, unified dataset, processing map + model, findings report).
- **Task typing**: Task 01 assigned `literature` (its dominant activity is literature search/extraction, not data transformation); Task 02 and Task 03 assigned `data-analysis` (both are Python/pandas/scipy-driven); Task 04 assigned `writing`.
- **Autonomous-mode assumptions substituted for checkpoints** (in place of what would normally be an AskUserQuestion interview per task):
  - Minimum corpus threshold (≥8 studies, ≥80 datapoints) — a heuristic power-of-regression rule, not user-confirmed; may need revisiting once Task 01 is underway if literature proves sparser than expected (per Gap 3 data-sparsity concern).
  - VED formula standardization (P/(v·h·t), recomputed uniformly rather than trusting source-reported VED) — chosen because LITERATURE.md flags VED-definition inconsistency across sources as a known confound.
  - Leave-one-study-out (not random k-fold) cross-validation — chosen specifically to test cross-platform/cross-study generalizability, which is this project's central novel claim (per LITERATURE.md: "no existing benchmark exists to validate methodology against").
  - "Validated processing map" defined as an internal (not external-benchmark) success criterion, since LITERATURE.md explicitly notes no prior cross-study quantification exists to benchmark against.
  - Archimedes-density-only rows retained for bulk-density trend checks but excluded from defect-type/classification analysis, since Archimedes cannot discriminate porosity from LOF (per LITERATURE.md methodological landscape notes).
- **First checkpoint**: placed after Task 01 (literature extraction). This is the natural human-verify point because the actual achieved corpus size/quality directly determines whether Tasks 02-03's statistical assumptions (minimum datapoint count, cross-validation feasibility) remain valid — if the corpus falls well short of the ≥8-study/≥80-datapoint target, the researcher should decide whether to expand search scope, lower rigor expectations, or descope Task 03's cross-validation ambitions before investing in cleaning/analysis.
- **Resource feasibility**: no VIRTUAL-LAB.md resource gaps block any of the 4 tasks — all required tooling (Python/pandas/numpy/scipy/matplotlib, manual bibliography tracking, opportunistic PDF-table extraction with manual-transcription fallback) is confirmed available or has an explicit fallback already built into the task assumptions above. No tasks flagged BLOCKED or ⚠.
