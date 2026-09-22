---
name: wtfms-research-explorer
description: "Synthesize candidate materials-science questions and write researcher-confirmed identity."
---

Load the linked references when their domain or template is needed. Resolve
them from this skill directory; their contents are copied verbatim from Daisy's
canonical research resources. Researcher questions belong to the orchestrator.

- [research-domains.md](references/research-domains.md)
- [RESEARCH.md](references/RESEARCH.md)
- [config.json](references/config.json)

## What Makes a Good Research Prompt

A good research prompt is:
- **Specific**: Names specific material, property, condition, or phenomenon
- **Answerable**: Can be confirmed or refuted by an achievable experiment or calculation
- **Novel**: Not already fully answered in the literature (this comes from literature-review, but initial framing matters)
- **Scoped**: Has clear in/out boundaries so the researcher knows when they're done

Bad: "Study high-entropy alloys"
Better: "Characterize mechanical properties of HEAs"
Good: "How does Cr content affect yield strength and ductility in CoCrFeMnNi alloys processed by arc melting?"

## Socratic Narrowing Is the Orchestrator's Job

The interview narrows in five moves: domain, then property or phenomenon, then conditions and processing route, then hypothesis, then explicit out-of-scope. The orchestrator runs those rounds. You read the transcript and judge whether the narrowing went far enough. If it did not, say exactly which move is missing and what to ask.

Do not fill gaps with assumptions. Vague prompts lead to unfocused research.



Generate three candidate research prompts at different levels of ambition. For each, propose a scope and keywords so the researcher can decide in one turn:

**Option A (Focused):** Narrowest, most achievable for the stated timeline and resources
**Option B (Standard):** Moderate scope, typical for a journal article
**Option C (Ambitious):** Broader, suitable if timeline and resources allow

For every option include:
- The prompt as one specific, answerable question
- In scope: 3 to 5 concrete items (materials, phenomena, conditions, methods)
- Out of scope: 2 to 4 explicit exclusions
- Keywords: 5 to 8 terms, marked primary or secondary
- Feasibility note: one line on why it fits (or strains) the stated resources and timeline

Return candidates in the mutation-report summary with the candidates_ready: prefix; write no files.


