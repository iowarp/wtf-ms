---
name: wtfMS:identify-research
description: Start exploring a research subject — guided interview to select fields, define scope, and generate a research prompt
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<execution_context>
@.claude/wtf-ms/templates/RESEARCH.md
@.claude/wtf-ms/references/research-domains.md
</execution_context>

<objective>
Initialize a new material science research project through deep guided interview. Creates `.research/` directory and populates RESEARCH.md with domain, sub-field, scope, researcher profile, and a confirmed research prompt.

**Orchestrator role:** Check preconditions, detect existing research context, gather research identity through batched questioning, spawn wtfms-research-explorer agent, commit result.

**Why subagent:** Research framing requires sustained Socratic dialogue and domain reasoning across material science areas. Fresh agent context = sharper prompt generation.
</objective>

<context>
No arguments. Runs in current directory.
</context>

<process>

## 1. Validate Environment

```bash
[ -f .research/RESEARCH.md ] && echo "WARN: Research already initialized." && echo "Use /wtfMS:progress to see current state, or continue to refine."
```

Initialize git if needed:
```bash
[ -d .git ] || git init
```

Create directory structure:
```bash
mkdir -p .research/tasks .research/data .research/checkpoints
```

## 2. Detect Existing Context

```bash
find . -name "*.pdf" -o -name "*.csv" -o -name "*.bib" -o -name "*.txt" 2>/dev/null | grep -v ".research" | grep -v ".claude" | grep -v ".git" | head -10
```

If data files found: ask via AskUserQuestion whether to base the research framing on existing files.

## 3. Gather Research Foundation (Batched)

Use AskUserQuestion — collect core framing in one turn:
- header: "Research Exploration — Material Science"
- question: "Let's explore your research direction.\n\n1. **Domain**: Which area of material science? (e.g., Structural, Energy, Biomaterials, Computational, Nanomaterials, Functional, Polymers, Characterization)\n2. **Driving question**: What phenomenon, material, or problem interests you? (free-form, even vague is fine)\n3. **Motivation**: Fundamental understanding, application/device, optimization, or review/synthesis?\n4. **Resources available**: Experimental lab, computational cluster, literature only, or combination?"
- options: "Provided details" | "I'm not sure yet — help me explore" | "I have a specific topic already"

**If "I'm not sure yet":** Ask about domain first, then walk through sub-fields in that domain using research-domains.md as reference.

**If "I have a specific topic already":** Jump to Step 5 (scope refinement).

## 4. Gather Researcher Profile

Use AskUserQuestion:
- header: "Researcher Context"
- question: "Help me understand your context:\n1. **Career stage**: Undergrad / Grad student / Postdoc / PI / Industry researcher\n2. **Timeline**: How long for this research? (months)\n3. **Prior work**: Have you already read papers in this area? Any specific authors or groups you follow?\n4. **Constraints**: Any materials, methods, or approaches you CANNOT use?"
- options: "Provided details" | "Skip — use reasonable defaults"

## 5. Spawn wtfms-research-explorer Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► EXPLORING RESEARCH SPACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Spawn with full inlined context:
```
Task(
  prompt="First, read .claude/agents/wtfMS/research-explorer.md for your role.\n\n" + filled_prompt,
  subagent_type="general-purpose",
  description="Research Exploration Interview"
)
```

Filled prompt includes:
- `<researcher_input>` — all answers gathered in Steps 3–4
- `<domains_ref>` — relevant section from research-domains.md
- `<research_path>` — target file: `.research/RESEARCH.md`

## 6. Handle Agent Return

**`## RESEARCH IDENTIFIED`:**
- Confirm RESEARCH.md was written
- Commit:
  ```bash
  git add .research/
  git commit -m "research: initialize — [research prompt one-liner]"
  ```

**`## CHECKPOINT REACHED`:**
- Present decision/question to user, collect response, resume

**`## EXPLORATION INCONCLUSIVE`:**
- Show what's missing, offer to re-run with more guidance

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► RESEARCH IDENTIFIED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prompt:  [selected research prompt]
Domain:  [field + sub-field]
Profile: .research/RESEARCH.md

───────────────────────────────────────────

## ▶ Next Up

**Conduct literature review and identify gaps**

`/wtfMS:literature-review`

───────────────────────────────────────────

**Also available:**
- `/wtfMS:upload-data` — attach existing datasets or papers first
- `/wtfMS:define-research-tasks` — skip literature review if already done

</offer_next>

<success_criteria>
- [ ] Domain and sub-field clearly identified
- [ ] Research prompt is a single answerable question
- [ ] Scope (in/out) explicitly defined
- [ ] Researcher profile captured (career stage, resources, timeline)
- [ ] At least 2 alternative prompts generated before final selection
- [ ] RESEARCH.md written using template
- [ ] Committed to git
</success_criteria>
