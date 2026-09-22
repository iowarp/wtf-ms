---
description: "Conduct literature review, identify research gaps, and define search keywords"
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
@.research/RESEARCH.md
@.research/config.json
</execution_context>

<objective>
Conduct a structured literature review based on the research identity in RESEARCH.md. Identifies current state of knowledge, open gaps, key authors/groups, and proposes refined search keywords. Creates LITERATURE.md.

**Orchestrator role:** Validate RESEARCH.md exists, gather the supplied corpus and scope guidance from the user, spawn the wtfms-literature-reviewer agent, run the advisory citation check, collect the researcher's decisions on flagged entries and proposed keywords, handle loop-back to identify-research if a major problem with the prompt is found.

**Why subagent:** Literature synthesis requires sustained reading, cross-referencing, and gap reasoning across many papers. Fresh context = more rigorous gap analysis. The agent never asks the researcher anything; every decision comes back here.
</objective>

<context>
No arguments. Reads .research/RESEARCH.md and .research/config.json.
</context>

<process>

Worker write scope: .research/LITERATURE.md.


## 1. Gather Supplied Materials First

Before any other research read, use ls on `.research/data/` and read
`.research/DATA-INDEX.md`; inspect readable registered materials first. Record
unreadable formats as access limits and ask for usable text when needed. Then
validate the research identity and config below.

### Validate Environment

```bash
[ ! -f .research/RESEARCH.md ] && echo "ERROR: No RESEARCH.md. Run /wtfMS:identify-research first." && exit 1
[ -f .research/LITERATURE.md ] && echo "WARN: LITERATURE.md exists. Running again will update it."
cat .research/RESEARCH.md
grep -q '"web_search": *false' .research/config.json 2>/dev/null && echo "WEB: disabled by config" || echo "URL FETCH: allowed"
```

## 2. Gather the Supplied Corpus

```bash
ls -la .research/data/ 2>/dev/null
cat .research/DATA-INDEX.md 2>/dev/null
```

Supplied papers, BibTeX files, and notes are the primary corpus for the review; researcher-provided URLs may extend it. If nothing is registered, say so in the scope question below and offer `/wtfMS:upload-data` first. Clio has no web search tool. State that the review is built from supplied
materials plus any specific URLs the researcher provides. Ask for those URLs in
the scope question; use web_fetch only when web_search is true and the tool is
available. With web_search false, use supplied materials only. Record this exact
coverage and access limits in LITERATURE.md under Sources Reviewed.

## 3. Confirm Scope with User

Use ask_user:
- header: "Literature Review Scope"
- question: "I'll review literature based on your research prompt:\n\n**[research prompt from RESEARCH.md]**\n\nCorpus: [N] supplied files [list] · Provided-URL fetching: [allowed|disabled]\n\nAnything to adjust before I start?\n1. Any specific papers, authors, or groups to prioritize?\n2. Any journals or conferences to focus on?\n3. Year range? (default: all years, emphasis on last 10)\n4. Any sub-topics to explicitly include or exclude?\n5. Any specific URLs to add to the supplied corpus?"
- options: "Start with current scope" | "I'll add more context" | "Upload papers first — /wtfMS:upload-data"

## 4. Spawn wtfms-literature-reviewer Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► REVIEWING LITERATURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use dispatch with `agent: "wtfms-literature-reviewer"` and a task containing the assignment and full context. The prompt carries:
- `<research>` — full RESEARCH.md content
- `<uploaded_data>` — every registered file path with its DATA-INDEX.md description
- `<user_guidance>` — scope adjustments from Step 3
- `<web_allowed>` — true only when config permits URL fetching and web_fetch is available
- `<provided_urls>` — the specific URLs supplied by the researcher, or none
- `<literature_path>` — `.research/LITERATURE.md`

## 5. Handle Agent Return

**`literature_review_complete:`:**

1. Use read on `.research/LITERATURE.md` and verify the file is on disk:
   ```bash
   test -s .research/LITERATURE.md && echo OK || echo "ERROR: LITERATURE.md missing"
   ```
   If missing, re-dispatch the agent and say so; do not continue.

2. Advisory citation check. Verify the Key Papers table against Crossref to catch fabricated papers or dead DOIs. This is advisory; it never deletes anything on its own:
   ```bash
   if command -v python3 >/dev/null 2>&1; then
     citation_flags=()
     grep -q '"web_search": *false' .research/config.json 2>/dev/null && citation_flags=(--offline)
     python3 "${extensionRoot}/resources/scripts/verify_citations.py" "${citation_flags[@]}" .research/LITERATURE.md || true
   fi
   ```
   - If python3 is absent, skip silently. If every entry is UNVERIFIABLE with network errors, record the access limitation in Review Notes and continue. With web_search false, run only the offline structural check.
   - If any entry is **NOT_FOUND** or **MISMATCH**: show each flagged entry next to the closest Crossref match and ask via ask_user, one batched question:
     - header: "Citation Check"
     - question: "Crossref could not confirm [N] entries:\n\n1. [entry] → closest match: [title, year, DOI] (score [x])\n2. ...\n\nFor each: keep as-is, mark unverified, correct to the match, or remove?"
     - options: "Keep all, mark unverified" | "Correct to matches where shown" | "I'll decide per entry" | "Remove all flagged"
     Apply the decision to LITERATURE.md. A flagged entry is never removed without the researcher saying so.

3. Keyword gate. The agent proposed changes in the Refined Keywords section and in its return. Ask via ask_user:
   - header: "Keyword Refinement"
   - question: "Based on the literature, I suggest refining keywords:\n\nAdd: [terms]\nRemove: [terms]\nReplace: [old] → [new]\n\nAny adjustments?"
   - options: "Accept refined keywords" | "Keep original keywords" | "I'll adjust"
   Apply the accepted set to the Keywords section of RESEARCH.md.

4. Record (optional git):
   ```bash
   grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/LITERATURE.md .research/RESEARCH.md && git commit -m "research: literature review — [N] sources, [N] gaps identified"
   ```

**`loop_back:`:**
- Read LITERATURE.md back and run the same advisory citation check and researcher decision gate above before applying the loop-back decision.
- The reviewer found the prompt is too broad, too narrow, already answered, or rests on a false premise. LITERATURE.md was still written.
- Present the finding and its three suggested prompts.
- Ask via ask_user:
  - header: "Prompt Needs Revision"
  - question: "The literature shows: [finding].\n\nSuggested revisions:\n1. [narrowed]\n2. [adjacent gap]\n3. [replication/extension]\n\nHow do you want to proceed?"
  - options: "Narrow to suggestion 1" | "Narrow to suggestion 2" | "Narrow to suggestion 3" | "Proceed with the current prompt anyway"
- If a suggestion is chosen: update the Selected Prompt and Key Decisions in RESEARCH.md and STATE.md, note the revision reason, then run the keyword gate above. If the change is larger than a rewording, recommend re-running `/wtfMS:identify-research` with the new framing.

**`needs_input: checkpoint:decision` or `needs_input: checkpoint:human-action`:**
- Present the question to the user, collect the answer via ask_user, re-dispatch the agent.

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► LITERATURE REVIEW COMPLETE ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review:   .research/LITERATURE.md
Sources:  [N] supplied, [N] researcher-provided URLs fetched
Gaps:     [N] identified
Keywords: [primary keywords]
Citations: [N verified, N marked unverified]

───────────────────────────────────────────

## ▶ Next Up

**Map your available lab resources**
(equipment, HPC, software, collaborations)

`/wtfMS:define-virtual-lab`

<sub>Each dispatch starts with fresh worker context.</sub>

───────────────────────────────────────────

**Also available:**
- `/wtfMS:identify-research` — refine prompt based on gaps found
- `/wtfMS:upload-data` — add more papers/datasets to review
- `/wtfMS:define-research-tasks` — skip virtual lab setup and go straight to workflow

</offer_next>

<success_criteria>
- [ ] Every question to the researcher was asked by this command, not by the agent
- [ ] Supplied corpus listed and passed to the agent; web availability passed explicitly
- [ ] Current state of knowledge summarized by sub-topic
- [ ] At least 3 research gaps identified and justified
- [ ] Key papers listed with quoted titles and provenance
- [ ] Citation check run; flagged entries decided by the researcher, never auto-removed
- [ ] Keywords refined only after the researcher accepted
- [ ] Loop-back handled if the prompt needs revision
- [ ] LITERATURE.md verified on disk; commit only if commit_research is true
</success_criteria>
