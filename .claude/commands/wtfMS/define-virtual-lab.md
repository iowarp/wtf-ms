---
name: wtfMS:define-virtual-lab
description: Interview to map all available lab resources — equipment, HPC, software, collaborations — into a VIRTUAL-LAB.md that guides feasible task planning
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
@.claude/wtf-ms/templates/VIRTUAL-LAB.md
</execution_context>

<objective>
Build a complete map of the researcher's available resources by conducting a structured interview. The resulting VIRTUAL-LAB.md is used by define-research-tasks and execute-task to ensure workflow steps are feasible and protocols match available equipment.

**Orchestrator role:** Load research context to ask targeted questions about relevant resources, spawn wtfms-lab-definer agent for the interview, write VIRTUAL-LAB.md, commit.

**Why subagent:** Resource interviews benefit from sustained cross-referencing — the agent reads what methods are common in the research field (from LITERATURE.md) and proactively asks about the most relevant equipment, avoiding a generic checklist that misses domain-specific tools.
</objective>

<context>
No arguments. Reads .research/RESEARCH.md and LITERATURE.md to ask targeted resource questions.
</context>

<process>

## 1. Validate Environment

```bash
[ ! -f .research/RESEARCH.md ] && echo "ERROR: No RESEARCH.md. Run /wtfMS:identify-research first." && exit 1
[ -f .research/VIRTUAL-LAB.md ] && echo "WARN: VIRTUAL-LAB.md already exists — running again will update it."
cat .research/RESEARCH.md
cat .research/LITERATURE.md 2>/dev/null | head -60
```

## 2. Quick Mode vs Full Interview

Use AskUserQuestion:
- header: "Virtual Lab Setup"
- question: "I'll map your available research resources. How would you like to proceed?\n\n**Quick**: Paste or describe all your resources in one response (I'll structure it)\n**Guided**: I'll interview you by category (equipment, computing, software, collaborations)\n\nI'll cross-reference with the methods commonly used in your field ([domain from RESEARCH.md]) to make sure I ask about the most relevant tools."
- options: "Quick — I'll describe everything at once" | "Guided interview by category"

## 3. Spawn wtfms-lab-definer Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► DEFINING VIRTUAL LAB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Spawn with full inlined context:
```
Task(
  prompt="First, read .claude/agents/wtfMS/lab-definer.md for your role.\n\n" + filled_prompt,
  subagent_type="general-purpose",
  description="Define Virtual Lab Resources"
)
```

Filled prompt includes:
- `<research>` — full RESEARCH.md (domain, prompt, scope)
- `<literature>` — LITERATURE.md methodological landscape section
- `<mode>` — "quick" or "guided" from Step 2
- `<user_input>` — free-text resource description (if quick mode)
- `<lab_path>` — target: `.research/VIRTUAL-LAB.md`

## 4. Handle Agent Return

**`## VIRTUAL LAB DEFINED`:**
- Commit:
  ```bash
  git add .research/VIRTUAL-LAB.md
  git commit -m "research: virtual lab defined — [N] equipment, [N] compute resources"
  ```

**`## CHECKPOINT REACHED`:**
- Present question to user, collect response, resume

## 5. Show Resource Summary

After VIRTUAL-LAB.md is written, display a summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► VIRTUAL LAB DEFINED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Experimental:  [N] equipment items ([key ones])
Computational: [HPC systems] + [local/cloud]
Software:      [key licenses]
External:      [N] facilities/collaborations

Resource gaps flagged: [N]
  → [e.g., "No TEM access — XRD is in-house"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► VIRTUAL LAB DEFINED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Lab profile: .research/VIRTUAL-LAB.md

───────────────────────────────────────────

## ▶ Next Up

**Build your research workflow**
(now resource-aware — tasks will only use available equipment)

`/wtfMS:define-research-tasks`

<sub>`/clear` first → fresh context window</sub>

───────────────────────────────────────────

**Also available:**
- `/wtfMS:upload-data` — register existing datasets before planning tasks
- `/wtfMS:literature-review` — continue reviewing if not complete

</offer_next>

<success_criteria>
- [ ] Domain-relevant equipment proactively asked about (from LITERATURE.md methods)
- [ ] Both experimental AND computational resources captured
- [ ] Software licenses documented
- [ ] External facilities and collaborations recorded
- [ ] Resource gaps identified and noted
- [ ] Resource-to-task mapping table populated
- [ ] VIRTUAL-LAB.md written and committed
</success_criteria>
