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
  - AskUserQuestion
---

<execution_context>
@.research/RESEARCH.md
@.research/config.json
</execution_context>

<objective>
Conduct a structured literature review based on the research identity in RESEARCH.md. Identifies current state of knowledge, open gaps, key authors/groups, and refines search keywords. Creates LITERATURE.md.

**Orchestrator role:** Validate RESEARCH.md exists, optionally gather additional context from user, spawn wtfms-literature-reviewer agent, handle loop-back to identify-research if major gap found.

**Why subagent:** Literature synthesis requires sustained reading, cross-referencing, and gap reasoning across many papers. Fresh context = more rigorous gap analysis.
</objective>

<context>
No arguments. Reads .research/RESEARCH.md.
</context>

<process>

## 1. Validate Environment

```bash
[ ! -f .research/RESEARCH.md ] && echo "ERROR: No RESEARCH.md. Run /wtfMS:identify-research first." && exit 1
[ -f .research/LITERATURE.md ] && echo "WARN: LITERATURE.md exists. Running again will update it."
cat .research/RESEARCH.md
```

## 2. Check for Uploaded Papers

```bash
ls .research/data/ 2>/dev/null | grep -E "\.pdf|\.bib|\.txt|\.csv" | head -10
```

If uploaded files exist: tell the reviewer agent to prioritize them.

## 3. Confirm Scope with User

Use AskUserQuestion:
- header: "Literature Review Scope"
- question: "I'll review literature based on your research prompt:\n\n**[research prompt from RESEARCH.md]**\n\nAnything to adjust before I start?\n1. Any specific papers, authors, or groups to prioritize?\n2. Any journals or conferences to focus on?\n3. Year range? (default: all years, emphasis on last 10)\n4. Any sub-topics to explicitly include or exclude?"
- options: "Start with current scope" | "I'll add more context" | "Upload papers first — /wtfMS:upload-data"

## 4. Spawn wtfms-literature-reviewer Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► REVIEWING LITERATURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Spawn with full context:
```
Task(
  prompt="First, read .claude/agents/wtfMS/literature-reviewer.md for your role.\n\n" + filled_prompt,
  subagent_type="general-purpose",
  description="Literature Review: [research sub-field]"
)
```

Filled prompt includes:
- `<research>` — full RESEARCH.md content
- `<uploaded_data>` — list of any uploaded papers/datasets
- `<user_guidance>` — scope adjustments from Step 3
- `<literature_path>` — target: `.research/LITERATURE.md`

## 5. Handle Agent Return

**`## LITERATURE REVIEW COMPLETE`:**
- Update RESEARCH.md with refined keywords (append to Keywords section)
- Commit:
  ```bash
  git add .research/LITERATURE.md .research/RESEARCH.md
  git commit -m "research: literature review — [N] papers, [N] gaps identified"
  ```

**`## LOOP BACK TO IDENTIFY-RESEARCH`:**
- The reviewer found that the research prompt is too broad, too narrow, or already fully answered
- Present the finding to user
- Ask via AskUserQuestion: refine prompt now or proceed anyway
- If refine: run `/wtfMS:identify-research` flow with pre-loaded context

**`## CHECKPOINT REACHED`:**
- Present decision to user, collect response, resume

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► LITERATURE REVIEW COMPLETE ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review:   .research/LITERATURE.md
Papers:   [N] reviewed
Gaps:     [N] identified
Keywords: [primary keywords]

───────────────────────────────────────────

## ▶ Next Up

**Map your available lab resources**
(equipment, HPC, software, collaborations)

`/wtfMS:define-virtual-lab`

<sub>`/clear` first → fresh context window</sub>

───────────────────────────────────────────

**Also available:**
- `/wtfMS:identify-research` — refine prompt based on gaps found
- `/wtfMS:upload-data` — add more papers/datasets to review
- `/wtfMS:define-research-tasks` — skip virtual lab setup and go straight to workflow

</offer_next>

<success_criteria>
- [ ] Current state of knowledge summarized by sub-topic
- [ ] At least 3 research gaps identified and justified
- [ ] Key papers listed with one-line descriptions
- [ ] Keywords refined from initial RESEARCH.md set
- [ ] Methodological landscape described (what approaches exist)
- [ ] Loop-back triggered if prompt needs revision
- [ ] LITERATURE.md written and committed
</success_criteria>
