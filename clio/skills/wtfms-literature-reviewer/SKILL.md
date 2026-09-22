---
name: wtfms-literature-reviewer
description: "Review supplied materials and provided URLs with citation provenance and explicit gaps."
---

Load the linked references when their domain or template is needed. Resolve
them from this skill directory; their contents are copied verbatim from Daisy's
canonical research resources. Researcher questions belong to the orchestrator.

- [research-domains.md](references/research-domains.md)
- [RESEARCH.md](references/RESEARCH.md)

## What a Good Literature Review Produces

1. **Knowledge map** — What is currently known, organized by sub-topic
2. **Methodological landscape** — What approaches exist, their strengths and limits
3. **Genuine gaps** — What remains unknown or contested, with justification
4. **Keyword refinement** — More precise terms than the initial set
5. **Key references** — Landmark papers and recent work (last 5 years)
6. **Loop-back signal** — Whether the research prompt needs adjustment

## Supplied Materials Come First

Papers, BibTeX files, and notes the researcher registered under `.research/data/` are the primary corpus. They anchor the review in the group's actual reading; record unsupported formats honestly. Researcher-provided URLs can extend that corpus when allowed. If `<web_allowed>` is false or the web tools are unavailable, review the supplied materials only and say so plainly in Review Notes. A review built from supplied materials alone is complete and honest; a review padded with invented papers is neither.

## Citation Integrity

Only list papers you actually read (supplied) or actually found (web) and are confident are real. Put each paper title in "quotes" in the Key Papers table and include a DOI when you have one, so the orchestrator can machine-verify the list against Crossref. If you are unsure a specific paper exists or only vaguely recall it, do not invent bibliographic details: omit it, or mark it `[topic — unverified, ~YEAR]` and note it under Review Notes. Flagged entries are shown to the researcher for a decision; they are not silently removed.

## Gap Quality

A genuine research gap is:
- **Specific**: "The fatigue behavior of HEAs at cryogenic temperatures" not "more research is needed"
- **Justified**: Supported by absence of papers or explicit statements in existing literature
- **Feasible**: Something the researcher's prompt could actually address

Not a gap: "Nobody has studied exactly this material system" (often because it's not interesting)

## Loop-Back Conditions

Signal `loop_back:` if:
- The prompt is already fully answered (>3 recent papers directly address it)
- The prompt is so broad it spans multiple review articles without a clear angle
- The prompt contains a false premise (assumed mechanism doesn't exist)

<clio_retrieval>
For literature work, inspect `.research/data/` and DATA-INDEX.md before other
research inputs or any network access. Read supplied papers, bibliographies and
notes first. If a binary/PDF cannot be read with available tools, record its path
and access limit and return a checkpoint for usable text when it blocks the task.
Do not claim full-text inspection from metadata or a filename.
Use web_fetch only for specific URLs the researcher supplied in <provided_urls>
and only when <web_allowed> is true and config does not set web_search false.
Clio has no web search tool. Do not invent URLs, issue search-provider queries,
or use bash as a search workaround. Record supplied files actually inspected,
URLs actually fetched, failed/unreadable sources and the restricted coverage in
Sources Reviewed. Missing coverage is not evidence that no literature exists.
</clio_retrieval>

