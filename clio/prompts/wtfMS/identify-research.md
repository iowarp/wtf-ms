---
description: "Start exploring a research subject — guided interview to select fields, define scope, and generate a research prompt"
---

<clio_execution>
Use read, ls, find and grep for file inspection, write/edit for state changes,
and bash for the shell blocks below. Treat $ARGUMENTS as operator text: parse the
command's documented arguments, validate task numbers as positive decimal
integers, and quote actual values in shell commands. Derive NN with printf '%02d'
from the decimal task number; use `.research/tasks/task-NN/` consistently.
Each bash call starts independently; bind actual N, NN, OUT, FILE or checkpoint
values in the same call that uses them. Do not assume shell variables persist.
Read reference files named in execution_context; @ paths are references to read,
not already-inlined file content. Keep project state in `.research/`.

For a command with researcher questions, check that ask_user is available
before running any process step that writes files.
Use ask_user(action="ask", max_rounds=24, questions=[{header:"...",
question:"...", options:[{label:"..."}]}]) for every question below. Preserve the
question text and choices, fill contextual brackets, and collect the researcher's
free text. Send at most four related question objects per round. Cancellation
stops dependent work. If ask_user is unavailable, stop at the first interview
gate before writes and report that this command needs an interactive session.
Close a completed interview with ask_user(action="complete", summary="...",
decisions=[{key:"research_decision",value:"the actual settled decision"}]);
record only answers actually supplied. Keep unresolved questions pending.

Run git add, git commit or git tag only after bash grep confirms
'"commit_research": *true' in `.research/config.json`; absent/false disables them.
Never run git init. Check existing git status first; preserve unrelated staged
changes and report a blocked/failed optional record honestly.
</clio_execution>

<clio_dispatch>
Select the named recipe with dispatch({agent:"wtfms-...", task:"assignment with
full context and exact permitted outputs", intent:{write_roots:["exact/output"]}}).
Replace the illustrative recipe/path with those stated in this command. Use the
registered dispatch fields shown here.
Read the recipe's bound skill references and inline required templates, domain
sections, answers and selected state into the worker task. Each dispatch starts
fresh: re-dispatch with the full original context, prior candidates/outputs and
the new selection, corrections, revisions or resume answer. Use monitor if the
returned run is still active. Do not infer a resumed transcript from a run ID.
Honor admission refusals instead of broadening write scope.

Agent returns are mutation-report JSON. Route on the beginning of summary using
the status branches below. For checkpoints, distinguish
`needs_input: checkpoint:decision` from `needs_input: checkpoint:human-action`;
ask the exact question(s), collect the answer and re-dispatch. No new top-level
status fields are allowed. A conforming JSON result is not proof of completion.
After EVERY dispatch that wrote, use ls and read on every reported output and on
the command's required files, including loop_back and partial checkpoint returns.
Verify nonempty content and the promised changes before presenting success or
continuing; re-dispatch with any missing/incorrect file named. Treat actual failed
validation or execution as failure even when summary claims completion.
</clio_dispatch>

<execution_context>
@${extensionRoot}/resources/templates/RESEARCH.md
@${extensionRoot}/resources/templates/config.json
@${extensionRoot}/resources/references/research-domains.md
</execution_context>

<objective>
Initialize a new material science research project through a deep guided interview. Creates `.research/` and populates RESEARCH.md with domain, sub-field, scope, researcher profile, and a confirmed research prompt.

**Orchestrator role:** Check preconditions, detect existing research context, run the whole researcher interview (foundation, profile, and Socratic drilling), spawn the wtfms-research-explorer agent for synthesis, present its candidate prompts, collect the choice, re-dispatch the agent to write the files, verify, record.

**Why the interview lives here:** Subagents cannot prompt the user on any host (Clio forbids ask_user in agent recipes). The orchestrator owns every question. The agent gets a fresh context window for the reasoning that benefits from it: turning the transcript into sharp, calibrated candidate prompts.
</objective>

<context>
No arguments. Runs in current directory.
</context>

<process>

Worker write scope: .research/RESEARCH.md and .research/STATE.md, only after selection.


## 1. Validate Environment

```bash
[ -f .research/RESEARCH.md ] && echo "WARN: Research already initialized. Use /wtfMS:progress to see current state, or continue to refine."
mkdir -p .research/tasks .research/data .research/checkpoints
[ -f .research/config.json ] || cp "${extensionRoot}/resources/templates/config.json" .research/config.json
```

wtf-MS never runs `git init`. Version control of `.research/` is the researcher's choice, controlled by `commit_research` in `.research/config.json` (default false).

## 2. Detect Existing Context

```bash
find . -name "*.pdf" -o -name "*.csv" -o -name "*.bib" -o -name "*.txt" 2>/dev/null | grep -v ".research" | grep -v ".claude" | grep -v ".git" | head -10
```

If data files found: ask via ask_user whether to base the research framing on existing files, and suggest `/wtfMS:upload-data` afterwards so the literature review can read them.

## 3. Gather Research Foundation (Batched)

Use ask_user — collect core framing in one turn:
- header: "Research Exploration — Material Science"
- question: "Let's explore your research direction.\n\n1. **Domain**: Which area of material science? (e.g., Structural, Energy, Biomaterials, Computational, Nanomaterials, Functional, Polymers, Characterization)\n2. **Driving question**: What phenomenon, material, or problem interests you? (free-form, even vague is fine)\n3. **Motivation**: Fundamental understanding, application/device, optimization, or review/synthesis?\n4. **Resources available**: Experimental lab, computational cluster, literature only, or combination?"
- options: "Provided details" | "I'm not sure yet — help me explore" | "I have a specific topic already"

**If "I'm not sure yet":** Ask about domain first, then walk through sub-fields in that domain using research-domains.md as reference, one ask_user per level, before continuing.

**If "I have a specific topic already":** Capture it verbatim, then go to Step 4 and run only Round 3 of Step 5.

## 4. Gather Researcher Profile

Use ask_user:
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

## 6. Dispatch wtfms-research-explorer

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► EXPLORING RESEARCH SPACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use dispatch with `agent: "wtfms-research-explorer"` and a task containing the assignment and full context. The prompt carries the full inlined context:
- `<researcher_input>` — the complete interview transcript from Steps 2–5
- `<domains_ref>` — the relevant section of research-domains.md
- `<research_path>` — `.research/RESEARCH.md`

Before selection, request candidates only and authorize no writes; omit
write_roots and say explicitly that this is the no-write candidate phase.
On selection, authorize exactly `.research/RESEARCH.md` and `.research/STATE.md`.
Include all three original candidates, the verbatim selection, scope corrections,
and the complete RESEARCH template in the writing dispatch.

## 7. Present Candidates and Collect the Choice

**`candidates_ready:`:**

Use ask_user, one turn:
- header: "Your Research Prompts"
- question: "Based on our conversation, here are 3 research prompts:\n\n**A (Focused):** [prompt A]\n  In: [scope] · Out: [scope] · Keywords: [list]\n\n**B (Standard):** [prompt B]\n  In / Out / Keywords\n\n**C (Ambitious):** [prompt C]\n  In / Out / Keywords\n\nRecommended: [X] because [reason].\n\nWhich fits your goals? If you pick one, also say whether its scope and keywords need any correction."
- options: "Prompt A" | "Prompt B" | "Prompt C" | "Combine or edit — I'll describe"

Re-dispatch the explorer with a `<selection>` block containing the choice and any corrections. Always spawn a fresh wtfms-research-explorer with the full `<researcher_input>` transcript plus `<selection>`.

**`needs_input: checkpoint:decision` or `needs_input: checkpoint:human-action`:** Ask the batched questions it lists via ask_user, append the answers to the transcript, and re-dispatch the agent.

**`exploration_inconclusive:`:** Show what's missing and what it suggested. Offer to re-run with more guidance.

## 8. Verify and Record

**`research_identified:`:**

```bash
test -s .research/RESEARCH.md && test -s .research/STATE.md && echo "OK: files on disk" || echo "ERROR: agent reported files it did not write"
grep -n "Selected Prompt" -A 2 .research/RESEARCH.md
```

If either file is missing, do not report success; re-dispatch the agent and tell it exactly which file is absent.

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

<sub>Each dispatch starts with fresh worker context.</sub>

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
