# wtf-MS

**Material Science Research Planning & Automation System**

A Claude Code command system that turns Claude into a structured material science research partner — built on the same framework as [wtf-p](https://github.com/akougkas/wtf-p) but specialized for the full research lifecycle: from exploring a research direction to conducting literature reviews, planning experiments or simulations, executing tasks, and writing the resulting paper.

## What It Does

Guides material science researchers through the full research pipeline:

```
/wtfMS:identify-research    → Interview-driven research framing: domain, prompt, scope
/wtfMS:literature-review    → Map current knowledge, identify gaps, refine keywords
/wtfMS:define-research-tasks → Build workflow from traditional templates + assumption interviews
/wtfMS:execute-task [N]     → Execute tasks: literature, experimental, computational, data-analysis
/wtfMS:wtfp                 → Bridge to wtf-p for paper writing with pre-filled context
```

## Core Loop

```
identify-research
      ↓
literature-review ←──────────────────────┐
      ↓                                   │ (loop back if prompt needs revision)
define-research-tasks                     │
      ↓
execute-task (repeat per task)
      ↓
wtfp (→ wtf-p paper writing system)
```

## All Commands

### Core Research Loop
| Command | What It Does |
|---------|-------------|
| `/wtfMS:identify-research` | Socratic interview → domain, research prompt, scope |
| `/wtfMS:literature-review` | Map knowledge, find gaps, refine keywords |
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
| `/wtfMS:pause-research` | Pause + auto-checkpoint |
| `/wtfMS:resume-research` | Resume from paused state |
| `/wtfMS:checkpoint save [label]` | Save state snapshot |
| `/wtfMS:checkpoint restore [tag]` | Restore snapshot |
| `/wtfMS:checkpoint list` | List snapshots |

### Meta
| Command | What It Does |
|---------|-------------|
| `/wtfMS:help` | Command reference |
| `/wtfMS:settings` | View/edit project config |

## Task Types

| Type | What the Executor Does |
|------|----------------------|
| `literature` | Search + synthesize papers → BibTeX + summary |
| `experimental` | Generate protocol + data recording template |
| `computational` | Generate input files + analysis scripts (DFT, MD, CALPHAD, etc.) |
| `data-analysis` | Write analysis code + results summary from uploaded data |
| `analytical` | Mathematical modeling, derivations, validation |
| `writing` | Bridge to `/wtfMS:wtfp` |

## Research Integrity

wtf-MS guards against the "plausible but wrong" failure modes of an LLM
research assistant with automated, advisory checks (they report and the agent
acts; they never hard-block):

- **Citation verification** — references are resolved against
  [Crossref](https://www.crossref.org/) to catch hallucinated papers and dead
  DOIs before they land in your research state.
  See [docs/verifying-citations.md](docs/verifying-citations.md).
- **Physical sanity checks** — generated task outputs are scanned for
  physically impossible values (below absolute zero, negative density,
  out-of-range fractions, compositions that don't sum to 100%).
  See [docs/checking-physics.md](docs/checking-physics.md).
- **Runnable-by-construction checks** — generated analysis/simulation scripts
  are parsed (never executed) to catch syntax errors, hallucinated imports, and
  silent stubs before you try to run them.
  See [docs/checking-scripts.md](docs/checking-scripts.md).

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
├── WORKFLOW.md      ← Tasks with status, assumptions, dependencies
├── STATE.md         ← Current position, phase, decisions
├── DATA-INDEX.md    ← Registered data files
├── config.json      ← Project settings
├── data/            ← Uploaded datasets and papers
└── tasks/
    ├── task-01/     ← Outputs per task
    ├── task-02/
    └── ...
```

## Integration with wtf-p

`/wtfMS:wtfp` translates your completed research into a wtf-p paper project. It:
- Pre-fills `.planning/PROJECT.md` from your research state
- Lets you choose which tasks/results to include or exclude
- Sets the core argument from your research findings
- Links source material back to `.research/` files

You never re-answer questions you already answered during research planning.

> **Requires wtf-p**: Install [wtf-p](https://github.com/akougkas/wtf-p) locally before using `/wtfMS:wtfp`.

## Installation

Copy into your project's `.claude/` directory:

```bash
cp -r .claude/commands/wtfMS   YOUR_PROJECT/.claude/commands/
cp -r .claude/agents/wtfMS     YOUR_PROJECT/.claude/agents/
cp -r .claude/wtf-ms           YOUR_PROJECT/.claude/
```

Then open Claude Code in your project and run `/wtfMS:help`.

## Architecture

```
User
 │
 ▼
Command (thin orchestrator)
 │   Reads .research/ state
 │   Asks targeted questions via AskUserQuestion
 │   Spawns agent with full inlined context
 ▼
Agent (heavy work, fresh context window)
 │   wtfms-research-explorer    → Socratic interview → RESEARCH.md
 │   wtfms-literature-reviewer  → Web search + synthesis → LITERATURE.md
 │   wtfms-workflow-planner     → Template + assumptions → WORKFLOW.md
 │   wtfms-task-executor        → Type-routed execution → task outputs
 ▼
.research/ (project state)
```

**Key design principle**: Each agent spawns in a fresh context window. This means complex reasoning (literature synthesis, assumption elicitation, protocol generation) happens at peak quality, unaffected by earlier conversation history.

## License

MIT
