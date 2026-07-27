# Verifying citations

An LLM research assistant's most damaging failure mode is a **plausible but
fabricated citation** — a real-sounding title, authors, and journal for a paper
that does not exist, or a well-formed DOI that resolves to nothing. wtf-MS
guards against this with an automated checker that resolves every citation
against [Crossref](https://www.crossref.org/), the scholarly DOI registry.

## What it does

`.claude/wtf-ms/scripts/verify_citations.py` reads `LITERATURE.md` and/or
`.bib` files, extracts citation candidates (BibTeX entries, and quoted paper
titles from the "Key Papers" tables), looks each one up in Crossref by DOI or
by title + author + year, and classifies it:

| Status | Meaning |
|--------|---------|
| `VERIFIED` | Matched a real published work (title similar, year consistent). |
| `MISMATCH` | A work was found but the metadata disagrees — wrong year, or only a weak title match. Needs a human look. |
| `NOT_FOUND` | No plausible match, or a DOI Crossref 404s. **Likely hallucinated.** |
| `UNVERIFIABLE` | No title to check (a placeholder like `[ML disc. 2024]`), or the network was unavailable. |

It exits non-zero if any `NOT_FOUND` or `MISMATCH` is present.

## When it runs

It runs automatically as an **advisory** step — it reports, and the command or
agent acts on the results; it never hard-blocks the workflow (Crossref or the
network can be flaky).

- `/wtfMS:literature-review` runs it on `.research/LITERATURE.md` before
  committing the review.
- `/wtfMS:execute-task` runs it on a completed task's `.bib` / reference output.

The response policy:

- **NOT_FOUND** → remove or replace the citation and re-search for a real
  source; never leave it in.
- **MISMATCH** → surface to the user next to the Crossref match to decide.
- **UNVERIFIABLE placeholder** → annotate as needing finalization before citing.

## Running it manually

```bash
# Verify a review (needs network for the Crossref lookups)
python3 .claude/wtf-ms/scripts/verify_citations.py .research/LITERATURE.md

# A task's references
python3 .claude/wtf-ms/scripts/verify_citations.py .research/tasks/task-01/*.bib

# Structural checks only, no network
python3 .claude/wtf-ms/scripts/verify_citations.py --offline .research/LITERATURE.md

# Machine-readable output
python3 .claude/wtf-ms/scripts/verify_citations.py --json .research/LITERATURE.md
```

Zero dependencies (Python stdlib only). Crossref needs no API key.

## How the behavior is tested

The extraction and classification logic is pinned by
`tests/test_verify_citations.py` (network-mocked, runs in CI). Those tests lock
in the tricky cases that were tuned by hand: quoted *emphasis phrases* in prose
must not be mistaken for titles, abbreviated titles (`"…in LPBF"`) are rescued
by author + year corroboration, compound surnames (`Scipioni Bertoli`) match,
and a 404'd DOI is reported as fabricated rather than as a network error.

## Limitations

- Crossref covers most journals and conferences but not everything — a
  legitimate paper in an unindexed venue, preprint server, or book can come
  back `MISMATCH`/`NOT_FOUND`. Treat those as "verify by hand", not "delete".
- Verification confirms a paper *exists*; it does not confirm the paper
  *supports the claim* it is cited for. That judgment stays with the researcher.
