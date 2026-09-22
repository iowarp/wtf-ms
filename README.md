# wtf-MS

**Material Science Research Planning & Automation System**

A Claude Code command system that turns Claude into a structured material science research partner — built on the same framework as [wtf-p](https://github.com/akougkas/wtf-p) but specialized for the full research lifecycle: from exploring a research direction to conducting literature reviews, mapping the lab you actually have, planning experiments or simulations, executing tasks, and handing the result to wtf-p for the paper.

## What It Does

Guides material science researchers through the full research pipeline:

```
/wtfMS:identify-research     → Interview-driven research framing: domain, prompt, scope
/wtfMS:literature-review     → Map current knowledge, identify gaps, refine keywords
/wtfMS:define-virtual-lab    → Map equipment, HPC, software, collaborations → feasibility
/wtfMS:define-research-tasks → Build workflow from traditional templates + assumption interviews
/wtfMS:execute-task [N]      → Execute tasks: literature, experimental, computational, data-analysis
/wtfMS:wtfp                  → Bridge to wtf-p for paper writing with pre-filled context
```

## Core Loop

```
identify-research
      ↓
literature-review ←──────────────────────┐
      ↓                                   │ (loop back if prompt needs revision)
define-virtual-lab                        │
      ↓
define-research-tasks   (resource-aware: flags tasks the lab cannot do)
      ↓
execute-task (repeat per task; guardrails after each)
      ↓
wtfp (→ wtf-p paper writing system)
```

## All Commands

### Core Research Loop
| Command | What It Does |
|---------|-------------|
| `/wtfMS:identify-research` | Socratic interview → domain, research prompt, scope |
| `/wtfMS:literature-review` | Supplied papers first, web second → knowledge map, gaps, keywords |
| `/wtfMS:define-virtual-lab` | Resource interview → VIRTUAL-LAB.md with gaps and alternatives |
| `/wtfMS:define-research-tasks` | Select workflow template, interview assumptions per task |
| `/wtfMS:execute-task [N\|all]` | Execute specific task or entire workflow |
| `/wtfMS:wtfp` | Bridge to wtf-p with include/exclude control |

### Task Management
| Command | What It Does |
|---------|-------------|
| `/wtfMS:add-task` | Add a task to the active workflow |
| `/wtfMS:remove-task [N]` | Remove a task permanently |
| `/wtfMS:archive-task [N]` | Archive (preserve but deactivate) |
| `/wtfMS:upload-data [file]` | Register data files, papers, datasets |

### Progress & Control
| Command | What It Does |
|---------|-------------|
| `/wtfMS:status` | Full project dashboard |
| `/wtfMS:progress` | Statusline + smart routing to next action |
| `/wtfMS:cost` | Token usage + estimated cost per step ([how it works](docs/recording-metrics.md)) |
| `/wtfMS:pause-research` | Pause + auto-checkpoint |
| `/wtfMS:resume-research` | Resume from paused state |
| `/wtfMS:checkpoint save [label]` | Save state snapshot |
| `/wtfMS:checkpoint restore [name]` | Restore snapshot |
| `/wtfMS:checkpoint list` | List snapshots |

### Meta
| Command | What It Does |
|---------|-------------|
| `/wtfMS:help` | Command reference |
| `/wtfMS:settings` | View/edit project config |

## Task Types

| Type | What the Executor Does |
|------|----------------------|
| `literature` | Read supplied papers, then search → BibTeX + summary |
| `experimental` | Generate protocol + data recording template + checklist |
| `computational` | Generate input files + analysis scripts (DFT, MD, CALPHAD, etc.) |
| `data-analysis` | Write analysis code + results summary from uploaded data |
| `analytical` | Mathematical modeling, derivations, validation |
| `writing` | Bridge to `/wtfMS:wtfp` |

## Research Domains Supported

- Structural materials (metals, HEAs, ceramics, composites)
- Energy materials (batteries, fuel cells, solar, hydrogen storage)
- Functional materials (semiconductors, magnetics, thermoelectrics)
- Biomaterials (scaffolds, implants, drug delivery)
- Nanomaterials (nanoparticles, graphene, 2D materials)
- Polymers and soft matter
- Computational materials science (DFT, MD, phase-field, CALPHAD)
- Characterization methods (SEM, TEM, XRD, APT, synchrotron)

## Traditional Workflow Templates

Built-in templates for:
1. Experimental research
2. Computational research
3. Integrated experimental + computational
4. Materials optimization / high-throughput
5. Literature review / meta-analysis
6. Device / application development

## Project State (`.research/`)

```
.research/
├── RESEARCH.md      ← Research identity, prompt, scope, keywords
├── LITERATURE.md    ← Review results, gaps, key papers
├── VIRTUAL-LAB.md   ← Equipment, HPC, software, external facilities, gaps
├── WORKFLOW.md      ← Tasks with status, assumptions, dependencies
├── STATE.md         ← Current position, phase, decisions
├── DATA-INDEX.md    ← Registered data files
├── config.json      ← Project settings
├── data/            ← Uploaded datasets and papers
├── checkpoints/     ← State snapshot archives (.tgz)
├── handoff/         ← Paste-ready blocks for wtf-p 0.6
└── tasks/
    ├── task-01/     ← Outputs per task
    ├── task-02/
    └── ...
```

## Configuration (`.research/config.json`)

| Key | Default | Effect |
|-----|---------|--------|
| `web_search` | `true` | Agents may search the web during literature work. Supplied papers are always read first. |
| `auto_checkpoint` | `true` | Save a `.research/checkpoints/` archive after each completed task. |
| `commit_research` | `false` | Let commands run `git add`/`commit`/`tag` on `.research/`. wtf-MS never runs `git init`. |
| `model_profile` | `balanced` | Reserved for hosts that route agents by profile. |
| `data_dir` | `.research/data` | Where uploaded files are copied. |

## Research Integrity (advisory guardrails)

After each `execute-task` (and after `literature-review`), the orchestrator runs three stdlib-only Python checks over the outputs and shows the findings. Nothing is removed or rewritten without the researcher's decision.

| Check | Catches | Docs |
|-------|---------|------|
| `check_physics.py` | Temperatures below absolute zero, non-positive densities, fractions outside 0–100, compositions that do not sum to 100 | [docs/checking-physics.md](docs/checking-physics.md) |
| `verify_citations.py` | Papers Crossref cannot find, dead DOIs, title/year mismatches | [docs/verifying-citations.md](docs/verifying-citations.md) |
| `check_scripts.py` | Python syntax errors, imports of packages that do not exist, stub bodies, leftover placeholders | [docs/checking-scripts.md](docs/checking-scripts.md) |

Requires `python3` (3.10+ preferred) on the PATH; if it is missing the checks are skipped and the workflow continues.

## Integration with wtf-p

`/wtfMS:wtfp` translates your research into a wtf-p paper project and detects which wtf-p you have:

- **wtf-p 0.6 and later** keeps schema-validated records under `.planning/` that only its own gated actions may create. The bridge writes `.research/handoff/` with three paste-ready blocks for `/wtfp:new-paper`, `/wtfp:map-project`, and `/wtfp:create-outline`, carrying your contribution, completed vs planned results, materials, locked and deferred decisions, and reference metadata with provenance. You approve each wtf-p gate yourself.
- **wtf-p 0.5** reads `.planning/PROJECT.md`; the bridge writes it and `config.json` directly.

You never re-answer questions you already answered during research planning.

> **Requires wtf-p**: `npx --yes --package=wtf-p@next -- wtf-p install claude` (or `clio`).

## Clio Coder

The same workflow ships as a hand-written [Clio Coder](https://github.com/iowarp/clio-coder) extension in [`clio/`](clio/README.md): the 17 `/wtfMS:*` prompts, six agent recipes, bound skills, a v4 execute-and-verify fleet, and the references, templates, and guardrail scripts as extension resources. Interviews run through Clio's `ask_user`, agents run through `dispatch`, and the same git policy applies. Clio has no web search tool, so literature work there is built from supplied papers plus researcher-provided URLs.

```bash
clio-coder extensions install ./clio --user        # requires Clio Coder >= 0.4.6
```

Install wtf-p's Clio extension beside it for the paper handoff. See [clio/README.md](clio/README.md).

## Installation (Claude Code)

wtf-MS is a Claude Code plugin. The repository root is the plugin root, so it
installs straight from a clone or from GitHub:

```bash
claude plugin marketplace add akougkas/wtf-ms
claude plugin install wtfMS@wtf-ms
```

From a local clone, point the marketplace at the checkout instead:

```bash
claude plugin marketplace add /path/to/wtf-ms
claude plugin install wtfMS@wtf-ms
```

Restart Claude Code, then run `/wtfMS:help`. Installed at user scope the
commands are available in every project; `--scope project` limits them to one.

The plugin name is `wtfMS` rather than kebab-case so the command namespace stays
`/wtfMS:*`. `claude plugin validate` warns about the casing, which only matters
for Claude.ai marketplace sync.

## Architecture

```
User
 │
 ▼
Command (orchestrator)
 │   Reads .research/ state
 │   Runs every interview via AskUserQuestion (batched)
 │   Spawns the registered agent with full inlined context
 │   Verifies the agent's files are on disk before reporting
 │   Runs advisory guardrails and shows findings
 │   Commits only if config.commit_research is true
 ▼
Agent (heavy work, fresh context window, never asks the user)
 │   wtfms-research-explorer    → candidates → RESEARCH.md + STATE.md
 │   wtfms-literature-reviewer  → supplied papers + web → LITERATURE.md
 │   wtfms-lab-definer          → structure + gap analysis → VIRTUAL-LAB.md
 │   wtfms-workflow-planner     → feasibility + ordering → WORKFLOW.md
 │   wtfms-task-executor        → type-routed execution → task outputs
 │   Returns COMPLETE | CHECKPOINT REACHED | BLOCKED; the command asks and resumes
 ▼
.research/ (project state)
```

**Key design principles**

- **Interviews live in the command.** Subagents cannot prompt the user on any host (Claude Code strips `AskUserQuestion` from subagents; Clio Coder forbids `ask_user` in agent recipes). Every question is asked by the orchestrator; agents return structured checkpoints when they need a decision.
- **Fresh context per agent.** Complex reasoning (literature synthesis, feasibility, protocol generation) happens at peak quality, unaffected by earlier conversation history.
- **Self-report is not completion.** A task is marked complete only after the orchestrator lists the output directory and reads the summary back.
- **Version control is the researcher's.** wtf-MS never runs `git init` and commits only when asked to in config.

## Development

```bash
python3 scripts/lint.py                                  # static checks on commands and agents
python3 -m unittest discover -s tests -p 'test_*.py'     # guardrail tests
```

CI runs both on every pull request ([.github/workflows/lint.yml](.github/workflows/lint.yml)). See [docs/linting.md](docs/linting.md).

## Credits

Created by Daisy Quach. Guardrail scripts and linter by Matthew Larson. Developed with the [IOWarp](https://iowarp.ai) project at the [Gnosis Research Center](https://grc.iit.edu/), Illinois Tech.

## License

MIT — see [LICENSE](LICENSE).
