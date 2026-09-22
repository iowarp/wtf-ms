---
name: wtfMS:identify-research
description: Start exploring a research subject — guided interview to select fields, define scope, and generate a research prompt
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

<execution_context>
@${CLAUDE_PLUGIN_ROOT}/wtf-ms/templates/RESEARCH.md
@${CLAUDE_PLUGIN_ROOT}/wtf-ms/templates/config.json
@${CLAUDE_PLUGIN_ROOT}/wtf-ms/references/research-domains.md
</execution_context>

<objective>
Initialize a new material science research project through a deep guided interview. Creates `.research/` and populates RESEARCH.md with domain, sub-field, scope, researcher profile, and a confirmed research prompt.

**Orchestrator role:** Check preconditions, detect existing research context, run the whole researcher interview (foundation, profile, and Socratic drilling), spawn the wtfms-research-explorer agent for synthesis, present its candidate prompts, collect the choice, resume the agent to write the files, verify, record.

**Why the interview lives here:** Subagents cannot prompt the user on any host (Claude Code strips AskUserQuestion from subagents; Clio forbids ask_user in agent recipes). The orchestrator owns every question. The agent gets a fresh context window for the reasoning that benefits from it: turning the transcript into sharp, calibrated candidate prompts.
</objective>

<context>
No arguments. Runs in current directory.
</context>

<process>

## 1. Validate Environment

```bash
[ -f .research/RESEARCH.md ] && echo "WARN: Research already initialized. Use /wtfMS:progress to see current state, or continue to refine."
mkdir -p .research/tasks .research/data .research/checkpoints
[ -f .research/config.json ] || cp ${CLAUDE_PLUGIN_ROOT}/wtf-ms/templates/config.json .research/config.json
```

wtf-MS never runs `git init`. Version control of `.research/` is the researcher's choice, controlled by `commit_research` in `.research/config.json` (default false).

## 2. Detect Existing Context

```bash
find . -name "*.pdf" -o -name "*.csv" -o -name "*.bib" -o -name "*.txt" 2>/dev/null | grep -v ".research" | grep -v ".claude" | grep -v ".git" | head -10
```

If data files found: ask via AskUserQuestion whether to base the research framing on existing files, and suggest `/wtfMS:upload-data` afterwards so the literature review can read them.

## 3. Gather Research Foundation (Batched)

Use AskUserQuestion — collect core framing in one turn:
- header: "Research Exploration — Material Science"
- question: "Let's explore your research direction.\n\n1. **Domain**: Which area of material science? (e.g., Structural, Energy, Biomaterials, Computational, Nanomaterials, Functional, Polymers, Characterization)\n2. **Driving question**: What phenomenon, material, or problem interests you? (free-form, even vague is fine)\n3. **Motivation**: Fundamental understanding, application/device, optimization, or review/synthesis?\n4. **Resources available**: Experimental lab, computational cluster, literature only, or combination?"
- options: "Provided details" | "I'm not sure yet — help me explore" | "I have a specific topic already"

**If "I'm not sure yet":** Ask about domain first, then walk through sub-fields in that domain using research-domains.md as reference, one AskUserQuestion per level, before continuing.

**If "I have a specific topic already":** Capture it verbatim, then go to Step 4 and run only Round 3 of Step 5.

## 4. Gather Researcher Profile

Use AskUserQuestion:
- header: "Researcher Context"
- question: "Help me understand your context:\n1. **Career stage**: Undergrad / Grad student / Postdoc / PI / Industry researcher\n2. **Timeline**: How long for this research? (months)\n3. **Prior work**: Have you already read papers in this area? Any specific authors or groups you follow?\n4. **Constraints**: Any materials, methods, or approaches you CANNOT use?"
- options: "Provided details" | "Skip — use reasonable defaults"

## 5. Socratic Drilling (as needed)

Narrow in up to three rounds. Skip any round whose answers the transcript already contains. Use the domain's sub-fields, key phenomena, and common methods from research-domains.md to make the examples concrete for this researcher.

**Round 1 — Narrow the sub-field:**
- header: "Narrowing Your Research Focus"
- question: "You mentioned [topic]. Let's narrow it down:\n\n1. What specific aspect? (e.g., for batteries: anode material? electrolyte? capacity fade mechanism? cycling stability?)\n2. What material system specifically? (e.g., Li-S, Na-ion, solid-state with sulfide electrolyte)\n3. What scale? (atomic/nano/micro/device level)"
- options: "Provided details" | "Help me choose — show sub-fields"

**Round 2 — Identify the gap:**
- header: "Finding the Angle"
- question: "For [narrowed topic]:\n1. What do you think is currently UNKNOWN or UNSOLVED?\n2. What would change if you answered your question? (better battery? new understanding? design rule?)\n3. What's your hypothesis or intuition about the answer?"
- options: "Provided details" | "I don't know yet — the literature review should tell me"

**Round 3 — Scope confirmation:**
- header: "Scoping the Research"
- question: "Final scoping:\n1. What methods will you use? (synthesis, characterization, simulation — be specific)\n2. What will you NOT study? (even if related and interesting)\n3. What's the minimum result that would make this a successful research project?"
- options: "Provided details" | "Let the candidates propose scope"

Assemble every answer from Steps 2 through 5, verbatim, into the `<researcher_input>` transcript.

## 6. Spawn wtfms-research-explorer Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► EXPLORING RESEARCH SPACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use the Agent tool with `subagent_type: wtfms-research-explorer` and `description: "Research Exploration"`. The prompt carries the full inlined context:
- `<researcher_input>` — the complete interview transcript from Steps 2–5
- `<domains_ref>` — the relevant section of research-domains.md
- `<research_path>` — `.research/RESEARCH.md`

## 7. Present Candidates and Collect the Choice

**`## CANDIDATES READY`:**

Use AskUserQuestion, one turn:
- header: "Your Research Prompts"
- question: "Based on our conversation, here are 3 research prompts:\n\n**A (Focused):** [prompt A]\n  In: [scope] · Out: [scope] · Keywords: [list]\n\n**B (Standard):** [prompt B]\n  In / Out / Keywords\n\n**C (Ambitious):** [prompt C]\n  In / Out / Keywords\n\nRecommended: [X] because [reason].\n\nWhich fits your goals? If you pick one, also say whether its scope and keywords need any correction."
- options: "Prompt A" | "Prompt B" | "Prompt C" | "Combine or edit — I'll describe"

Resume the same explorer agent with a `<selection>` block containing the choice and any corrections. If the host cannot resume an agent, spawn a fresh wtfms-research-explorer with the full `<researcher_input>` transcript plus `<selection>`.

**`## CHECKPOINT REACHED`:** Ask the batched questions it lists via AskUserQuestion, append the answers to the transcript, and resume (or re-spawn) the agent.

**`## EXPLORATION INCONCLUSIVE`:** Show what's missing and what it suggested. Offer to re-run with more guidance.

## 8. Verify and Record

**`## RESEARCH IDENTIFIED`:**

```bash
test -s .research/RESEARCH.md && test -s .research/STATE.md && echo "OK: files on disk" || echo "ERROR: agent reported files it did not write"
grep -n "Selected Prompt" -A 2 .research/RESEARCH.md
```

If either file is missing, do not report success; resume the agent and tell it exactly which file is absent.

Optional git record, only if the researcher enabled it:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/RESEARCH.md .research/STATE.md .research/config.json && git commit -m "research: initialize — [research prompt one-liner]"
```

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

**Register the papers you already have, then review the literature**

`/wtfMS:upload-data` (optional, but the review is only as good as its corpus)
`/wtfMS:literature-review`

───────────────────────────────────────────

**Also available:**
- `/wtfMS:define-research-tasks` — skip literature review if already done

</offer_next>

<success_criteria>
- [ ] Every question to the researcher was asked by this command, not by the agent
- [ ] Domain and sub-field clearly identified
- [ ] Research prompt is a single answerable question
- [ ] Scope (in/out) explicitly defined
- [ ] Researcher profile captured (career stage, resources, timeline)
- [ ] Three candidate prompts presented before final selection
- [ ] RESEARCH.md and STATE.md verified on disk with test -s
- [ ] config.json created from template; no git init; commit only if commit_research is true
</success_criteria>
