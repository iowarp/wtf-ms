---
name: wtfMS:wtfp
description: Bridge to wtf-p — translate research state into a paper project, with include/exclude control
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
@.research/WORKFLOW.md
@.research/STATE.md
</execution_context>

<objective>
Translate the completed (or in-progress) research state into a wtf-p paper project. Pre-populates .planning/PROJECT.md with research context so the user doesn't re-answer questions already answered during research planning.

**Orchestrator role:** Read all research state, ask what to include/exclude for the paper, generate pre-filled PROJECT.md and config.json, offer to launch /wtfp:create-outline.
</objective>

<context>
No arguments. Reads all .research/ state.
</context>

<process>

## 1. Validate Research State

```bash
[ ! -f .research/RESEARCH.md ] && echo "ERROR: No research initialized. Run /wtfMS:identify-research first." && exit 1
cat .research/RESEARCH.md
cat .research/LITERATURE.md 2>/dev/null | head -80
cat .research/WORKFLOW.md 2>/dev/null | head -60
```

Check .planning/ for existing wtf-p project:
```bash
[ -f .planning/PROJECT.md ] && echo "WARN: wtf-p project already exists at .planning/PROJECT.md"
```

## 2. Gather Task Outputs

```bash
find .research/tasks/ -name "*.md" -o -name "*.txt" -o -name "summary*" 2>/dev/null | head -20
```

List completed tasks and their output files so user knows what's available to include.

## 3. Determine Paper Scope

Use AskUserQuestion:
- header: "Paper Scope — What to Include"
- question: "I'll translate your research into a wtf-p paper project.\n\nYour completed tasks:\n[list of ☑ complete tasks]\n\n**What should the paper include?**\n1. Which tasks/results are IN the paper?\n2. Which results or methods are OUT of scope for this paper?\n3. **Venue**: Where are you submitting? (e.g., Acta Materialia, Nature Materials, ACS Nano, arxiv, conference)\n4. **Paper type**: Full research article? Letter? Review? Conference paper?"
- options: "Include all completed work" | "I'll specify inclusions" | "Exclude specific tasks"

## 4. Determine Paper Argument

Use AskUserQuestion:
- header: "Core Argument"
- question: "What is the ONE finding this paper must communicate?\n\n(This becomes the core argument in wtf-p's PROJECT.md. Be specific — not 'we studied X' but 'X enables Y because Z')"
- options: "Provided it" | "Help me formulate it from my research"

**If "Help me formulate it":** Read WORKFLOW.md task outputs + LITERATURE.md gaps and suggest 2–3 candidate core arguments. Let user select and refine.

## 5. Check wtf-p Installation

```bash
ls .claude/commands/wtfp/ 2>/dev/null | head -3 || echo "wtf-p not installed"
```

If not installed: warn user. Suggest installing wtf-p before proceeding.

## 6. Create .planning/ Structure

```bash
mkdir -p .planning/structure .planning/sections .planning/sources
```

## 7. Write Pre-filled PROJECT.md

Write `.planning/PROJECT.md` using wtf-p's project template format, populated from research state:

```markdown
# [Paper Title — derived from research prompt]

## What This Is
Type: [research article | letter | review | conference paper]
Venue: [venue from user input]
Core contribution: [core argument from Step 4]

## Core Argument
[ONE sentence thesis — the finding this paper proves]

## Requirements
### Must Have
[Included tasks/results from Step 3]

### Should Have
[Secondary results available]

### Out of Scope
[Explicitly excluded items from Step 3]

## Target Audience
[Derived from venue — e.g., "Materials scientists familiar with HEAs but not necessarily fatigue mechanics"]

## Constraints
- Deadline: [from RESEARCH.md timeline]
- Length: [venue-appropriate]
- Format: [venue-appropriate]
- Data availability: [what's been measured/computed]

## Key Decisions
[Locked decisions from research planning — e.g., "DFT used PBE functional", "all tests at room temperature"]

## Research Background (from wtfMS)
- Research prompt: [from RESEARCH.md]
- Gaps addressed: [from LITERATURE.md]
- Methodology: [from WORKFLOW.md tasks]
- Key results: [from completed task outputs]

## Source Material
[List of .research/ files to draw from]
```

## 8. Write config.json for wtf-p

Write `.planning/config.json` with default balanced settings. Set `venue_template` based on user's venue selection.

## 9. Commit

```bash
git add .planning/PROJECT.md .planning/config.json
git commit -m "docs: initialize paper from wtfMS research — [paper title]"
```

## 10. Offer Next Steps

Ask via AskUserQuestion:
- header: "Launch Paper Writing?"
- question: "Your paper project is ready at .planning/PROJECT.md.\n\nReady to start writing with wtf-p?"
- options: "Yes — run /wtfp:create-outline now" | "I'll review PROJECT.md first" | "Not yet"

If yes: trigger `/wtfp:create-outline` flow.

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► PAPER PROJECT INITIALIZED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: .planning/PROJECT.md
Source:  .research/ (research state preserved)

───────────────────────────────────────────

## ▶ Next Up (in wtf-p)

`/wtfp:create-outline`
`/wtfp:plan-section 1`

<sub>`/clear` first → fresh context window</sub>

───────────────────────────────────────────

</offer_next>

<success_criteria>
- [ ] All .research/ state read and summarized
- [ ] Include/exclude confirmed with user
- [ ] Core argument is one specific sentence (not vague)
- [ ] PROJECT.md pre-filled — user should not need to re-answer research questions
- [ ] Source material section links back to .research/ files
- [ ] Venue and paper type set
- [ ] config.json written with venue_template
- [ ] wtf-p installation confirmed before proceeding
</success_criteria>
