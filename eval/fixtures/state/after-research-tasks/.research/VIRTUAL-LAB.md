# Virtual Lab

## Experimental Facilities

### Labs Accessible
| Lab Type | Location/Name | Access Level | Notes |
|----------|--------------|--------------|-------|
| Chemistry/wet lab | N/A | N/A | No lab access (literature-only project) |
| Mechanical testing | N/A | N/A | No lab access (literature-only project) |
| Microscopy suite | N/A | N/A | No lab access (literature-only project) |
| Cleanroom | N/A | N/A | No lab access (literature-only project) |
| Processing/synthesis (LPBF machine) | N/A | N/A | No lab access (literature-only project) — all LPBF process-defect data sourced from published studies/datasets |

### Equipment Inventory

#### Characterization
| Equipment | Model/Capability | Access | Booking | Limitations |
|-----------|-----------------|--------|---------|-------------|
| XCT (X-ray computed tomography) | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | Porosity/LOF values extracted from published XCT results, not measured in-house |
| Archimedes density | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | Density/porosity values extracted from published data only |
| Optical/SEM metallography | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | Defect morphology data taken from published micrographs, not generated |
| Synchrotron/operando X-ray monitoring | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | Explicitly out of scope per LITERATURE.md; mechanistic in-situ data used only as cited literature findings |

#### Mechanical Testing
| Equipment | Capability | Access | Max Load | Temperature Range |
|-----------|-----------|--------|----------|-------------------|
| Universal testing machine | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | N/A |
| Fatigue tester | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | N/A |
| Hardness tester | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | N/A |

Note: Mechanical property modeling is explicitly out of scope for this project (per RESEARCH.md scope statement), so this category is doubly N/A — not needed even if access existed.

#### Processing / Synthesis
| Equipment | Type | Capability | Access |
|-----------|------|-----------|--------|
| LPBF/SLM machine | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A |
| Powder characterization equipment | N/A | N/A — no lab/HPC/external access (literature-only project) | N/A |

Note: No new experimental fabrication is in scope (per RESEARCH.md); this category is intentionally and permanently N/A for this project, not a gap.

---

## Computational Resources

### HPC Systems
| System Name | Cores Available | RAM/Node | Storage | Scheduler | Key Software |
|-------------|----------------|---------|---------|-----------|-------------|
| N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | N/A | N/A | N/A |

Note: ML/deep-learning approaches requiring HPC/GPU are explicitly out of scope (per RESEARCH.md); absence of HPC is an intentional constraint, not an oversight.

### Local Workstations
| Machine | CPU | GPU | RAM | OS | Special Use |
|---------|-----|-----|-----|----|-------------|
| Researcher's personal/work laptop | Unspecified (consumer-grade, sufficient for tabular stats) | Not required for this workload | Unspecified | Unspecified (Python cross-platform) | Primary and only workstation — literature synthesis, dataset cleaning, statistical regression, processing-map plotting |

### Cloud / External Compute
| Resource | Type | Cost Model | Access Method |
|----------|------|-----------|---------------|
| N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | N/A |

---

## Software Licenses
| Software | Purpose | License | Version | Notes |
|----------|---------|---------|---------|-------|
| Python | Core analysis language | open-source | Unspecified (assume 3.x) | Installed and available |
| pandas | Data wrangling / tuple extraction from literature-derived (P, v, h, t, VED, porosity) tables | open-source | Unspecified | Installed and available |
| numpy | Numerical computation | open-source | Unspecified | Installed and available |
| scipy | Statistical regression, curve fitting for VED/porosity relationships | open-source | Unspecified | Installed and available |
| matplotlib | Processing-map and defect-density visualization | open-source | Unspecified | Installed and available |
| Reference manager (e.g., Zotero) | Literature/citation management across many source papers | not yet confirmed installed | N/A | ⚠ Not explicitly mentioned by researcher — recommended addition given large literature-synthesis load; free/open-source, no license cost |
| PDF-mining/table-extraction tool (e.g., Tabula, camelot, pdfplumber) | Extracting (P, v, h, t, porosity) tuples from PDF tables in published papers | not yet confirmed installed | N/A | ⚠ Not explicitly mentioned by researcher — recommended addition; open-source Python-compatible (camelot/pdfplumber), fits existing stack with no new license needed |
| MATLAB | N/A | N/A | N/A | Explicitly not available — no commercial stats package (per researcher statement) |
| OriginPro | N/A | N/A | N/A | Explicitly not available — no commercial stats package (per researcher statement) |

---

## External Facilities & Collaborations
| Facility | Type | Access Route | Typical Lead Time | Contact |
|----------|------|-------------|-------------------|---------|
| N/A | N/A — no lab/HPC/external access (literature-only project) | N/A | N/A | N/A |

Note: No external collaborations or facility access, by explicit researcher statement — this is an intentional single-researcher project constraint, not a gap to flag.

### Public Data Repositories (literature-equivalent resource, not a facility)
| Source | Type | Access Route | Notes |
|--------|------|-------------|-------|
| Zenodo — "Processing, microstructure, mechanical property dataset for LPBF Ti-6Al-4V" | Public dataset (42 parameter sets) | Open download | Candidate primary data source per LITERATURE.md |
| PMC — "Dataset of process-structure-property feature relationship for LPBF Ti-6Al-4V" | Companion public dataset/paper | Open access | Candidate primary data source per LITERATURE.md |
| NIST AM-Bench | Public dataset repository | Open access (if relevant) | ⚠ Flagged in LITERATURE.md as needing further verification — relevance to Ti-6Al-4V porosity/LOF not yet confirmed |
| Institutional/personal journal access | Published literature | Researcher's own subscription/personal access | Used for VED-based processing map studies, dimensionless scaling law papers, ML porosity-prediction papers per LITERATURE.md methodological landscape |

---

## Materials & Consumables
- **Budget**: N/A — no physical materials procured (literature-only project)
- **Material sourcing**: N/A — no physical materials; all data sourced from published studies and public datasets
- **Typical lead time**: N/A
- **Storage**: N/A

---

## Human Resources
- **Personnel**: Single researcher (industry R&D context, likely independent or small-team project)
- **Time on this project**: Flexible, no hard deadline; part-time/as-available basis implied by industry R&D context
- **Key skills in lab**: Literature review and synthesis, Python-based statistical analysis (pandas/numpy/scipy/matplotlib), processing-map construction
- **Skills gaps**: None flagged for the in-scope statistical/meta-analysis workload; no ML/DL or HPC skills needed since those approaches are explicitly out of scope

---

## Constraints & Blockers
- **Primary standing constraint**: No experimental lab access of any kind — all porosity/LOF/process-parameter data must come from published papers and public datasets (Zenodo, PMC, NIST). This is an explicit, permanent project constraint, not a temporary blocker.
- **Primary standing constraint**: No HPC/cluster access — restricts analysis to laptop-scale statistical methods (regression, empirical VED-based maps); rules out ML/DL approaches requiring GPU/HPC by design (already out of scope).
- **Primary standing constraint**: No commercial software licenses (no MATLAB, no OriginPro, no commercial stats package) — all analysis must use the open-source Python stack (pandas, numpy, scipy, matplotlib).
- **Secondary/operational constraint**: Access to the full literature is limited to what the researcher's institutional/personal subscriptions cover; paywalled papers not accessible through personal access may need to be excluded or obtained via other means (e.g., interlibrary loan, author requests).
- **Secondary/operational constraint**: Heterogeneity across published (P, v, h, t, porosity) datasets (different measurement methods — XCT vs. Archimedes vs. metallography, different machines/powders) — a data-quality/harmonization issue for the meta-analysis, not a resource gap.
- No equipment currently down, no booking backlogs, no certifications needed, no export control/IP restrictions — all inapplicable given literature-only scope.

---

## Resource-to-Task Mapping
*Auto-generated during define-virtual-lab — maps available resources to WORKFLOW.md task types*

| Task Type | Required Resource | Available? | Alternative if Not |
|-----------|-----------------|------------|-------------------|
| Literature search / paper acquisition | Institutional/personal journal access | Yes | N/A |
| Dataset acquisition (Zenodo, PMC, NIST) | Internet access + browser/download tools | Yes | N/A |
| PDF table/figure data extraction (P, v, h, t, porosity tuples) | Python (pandas) + manual extraction; PDF-mining tool recommended | Yes (manual); ⚠ recommend adding camelot/pdfplumber for efficiency | Manual transcription if tool unavailable |
| Data cleaning / harmonization across studies | Python (pandas, numpy) | Yes | N/A |
| VED calculation (derived from P, v, h, t) | Python (numpy) | Yes | N/A |
| Statistical regression / correlation analysis (porosity vs. VED and other parameters) | Python (scipy, numpy) | Yes | N/A |
| Processing-map construction & visualization | Python (matplotlib) | Yes | N/A |
| Citation/reference management across many source papers | Reference manager (e.g., Zotero) | ⚠ Not confirmed installed | Manual bibliography tracking in spreadsheet/markdown if not adopted |
| XRD/XCT/SEM characterization (generating new defect data) | In-house or external equipment | No — out of scope | Use only published/extracted values; no in-house alternative needed |
| DFT / atomistic simulation | HPC + VASP/QE | No — out of scope | Not needed for this project's scope |
| ML/deep-learning porosity prediction (novel model training) | HPC/GPU | No — explicitly out of scope | Use simpler laptop-scale regression/statistical fits instead |
| Tensile/mechanical property testing or modeling | UTM or FEM software | No — out of scope | Not needed; mechanical property modeling excluded from scope |
| New experimental LPBF fabrication | LPBF machine + lab | No — out of scope | Not needed; synthesis of existing published data only |
