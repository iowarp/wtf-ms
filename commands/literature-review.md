---
name: wtfMS:literature-review
description: Conduct literature review, identify research gaps, and define search keywords
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
  - AskUserQuestion
---

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

## 1. Validate Environment

```bash
[ ! -f .research/RESEARCH.md ] && echo "ERROR: No RESEARCH.md. Run /wtfMS:identify-research first." && exit 1
[ -f .research/LITERATURE.md ] && echo "WARN: LITERATURE.md exists. Running again will update it."
cat .research/RESEARCH.md
grep -q '"web_search": *false' .research/config.json 2>/dev/null && echo "WEB: disabled by config" || echo "WEB: allowed"
```

## 2. Gather the Supplied Corpus

```bash
ls -la .research/data/ 2>/dev/null
cat .research/DATA-INDEX.md 2>/dev/null
```

Supplied papers, BibTeX files, and notes are the primary corpus for the review; the web extends it. If nothing is registered, say so in the scope question below and offer `/wtfMS:upload-data` first. On a host without web tools, or with `web_search` disabled, the review is built from supplied materials only.

## 3. Confirm Scope with User

Use AskUserQuestion:
- header: "Literature Review Scope"
- question: "I'll review literature based on your research prompt:\n\n**[research prompt from RESEARCH.md]**\n\nCorpus: [N] supplied files [list] · Web: [allowed|disabled]\n\nAnything to adjust before I start?\n1. Any specific papers, authors, or groups to prioritize?\n2. Any journals or conferences to focus on?\n3. Year range? (default: all years, emphasis on last 10)\n4. Any sub-topics to explicitly include or exclude?"
- options: "Start with current scope" | "I'll add more context" | "Upload papers first — /wtfMS:upload-data"

## 4. Spawn wtfms-literature-reviewer Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► REVIEWING LITERATURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use the Agent tool with `subagent_type: wtfms-literature-reviewer` and `description: "Literature Review: [research sub-field]"`. The prompt carries:
- `<research>` — full RESEARCH.md content
- `<uploaded_data>` — every registered file path with its DATA-INDEX.md description
- `<user_guidance>` — scope adjustments from Step 3
- `<web_allowed>` — true or false from Step 1
- `<literature_path>` — `.research/LITERATURE.md`

## 5. Handle Agent Return

**`## LITERATURE REVIEW COMPLETE`:**

1. Verify the file is on disk:
   ```bash
   test -s .research/LITERATURE.md && echo OK || echo "ERROR: LITERATURE.md missing"
   ```
   If missing, resume the agent and say so; do not continue.

2. Advisory citation check. Verify the Key Papers table against Crossref to catch fabricated papers or dead DOIs. This is advisory; it never deletes anything on its own:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/wtf-ms/scripts/verify_citations.py .research/LITERATURE.md || true
   ```
   - If the script is missing, python3 is absent, or every entry is UNVERIFIABLE with network errors: note that verification was skipped and continue.
   - If any entry is **NOT_FOUND** or **MISMATCH**: show each flagged entry next to the closest Crossref match and ask via AskUserQuestion, one batched question:
     - header: "Citation Check"
     - question: "Crossref could not confirm [N] entries:\n\n1. [entry] → closest match: [title, year, DOI] (score [x])\n2. ...\n\nFor each: keep as-is, mark unverified, correct to the match, or remove?"
     - options: "Keep all, mark unverified" | "Correct to matches where shown" | "I'll decide per entry" | "Remove all flagged"
     Apply the decision to LITERATURE.md. A flagged entry is never removed without the researcher saying so.

3. Keyword gate. The agent proposed changes in the Refined Keywords section and in its return. Ask via AskUserQuestion:
   - header: "Keyword Refinement"
   - question: "Based on the literature, I suggest refining keywords:\n\nAdd: [terms]\nRemove: [terms]\nReplace: [old] → [new]\n\nAny adjustments?"
   - options: "Accept refined keywords" | "Keep original keywords" | "I'll adjust"
   Apply the accepted set to the Keywords section of RESEARCH.md.

4. Record (optional git):
   ```bash
   grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/LITERATURE.md .research/RESEARCH.md && git commit -m "research: literature review — [N] sources, [N] gaps identified"
   ```

**`## LOOP BACK TO IDENTIFY-RESEARCH`:**
- The reviewer found the prompt is too broad, too narrow, already answered, or rests on a false premise. LITERATURE.md was still written.
- Present the finding and its three suggested prompts.
- Ask via AskUserQuestion:
  - header: "Prompt Needs Revision"
  - question: "The literature shows: [finding].\n\nSuggested revisions:\n1. [narrowed]\n2. [adjacent gap]\n3. [replication/extension]\n\nHow do you want to proceed?"
  - options: "Narrow to suggestion 1" | "Narrow to suggestion 2" | "Narrow to suggestion 3" | "Proceed with the current prompt anyway"
- If a suggestion is chosen: update the Selected Prompt and Key Decisions in RESEARCH.md and STATE.md, note the revision reason, then run the keyword gate above. If the change is larger than a rewording, recommend re-running `/wtfMS:identify-research` with the new framing.

**`## CHECKPOINT REACHED`:**
- Present the question to the user, collect the answer via AskUserQuestion, resume the agent.

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► LITERATURE REVIEW COMPLETE ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review:   .research/LITERATURE.md
Sources:  [N] supplied, [N] web
Gaps:     [N] identified
Keywords: [primary keywords]
Citations: [N verified, N marked unverified]

───────────────────────────────────────────

## ▶ Next Up

**Map your available lab resources**
(equipment, HPC, software, collaborations)

`/wtfMS:define-virtual-lab`

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
