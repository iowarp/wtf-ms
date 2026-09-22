# Verifying citations

An LLM research assistant's most damaging failure mode is a **plausible but
fabricated citation** — a real-sounding title, authors, and journal for a paper
that does not exist, or a well-formed DOI that resolves to nothing. wtf-MS
guards against this with an automated checker that resolves every citation
against [Crossref](https://www.crossref.org/), the scholarly DOI registry.

## What it does

`wtf-ms/scripts/verify_citations.py` reads `LITERATURE.md` and/or
`.bib` files, extracts citation candidates, looks each one up in Crossref by
DOI or by title, and classifies it:

| Status | Meaning |
|--------|---------|
| `VERIFIED` | Matched a real published work (title similar, year consistent). |
| `MISMATCH` | A work was found but the metadata disagrees — wrong year, or only a weak title match. Needs a human look. |
| `NOT_FOUND` | No plausible match, or a DOI Crossref 404s. **Likely hallucinated.** |
| `UNVERIFIABLE` | No title to check (a placeholder like `[ML disc. 2024]`), or the network was unavailable. |

It exits non-zero if any `NOT_FOUND` or `MISMATCH` is present. Every
`NOT_FOUND` and `MISMATCH` line carries the closest Crossref result (title and
DOI) so the reader can judge the flag without re-searching.

## What counts as a citation

Only three places in a Markdown document are scanned; prose is never scanned,
so a quoted emphasis phrase next to a year is not mistaken for a title.

- BibTeX entries, whether in a `.bib` file or a BibTeX block inside Markdown.
  These carry their own title, year, author, and DOI.
- Rows of the **Key Papers** table (header starts with `Paper`, or the table
  sits under a `## Key Papers` heading). The quoted string is the title and the
  year comes from the row. An author string is attached only when the row's
  first cell starts with an author list such as `King W.E. et al.`,
  `W.E. King and R. Smith`, or `Tang M., Pistorius P.C.`; otherwise the
  Crossref query is by title alone. Earlier versions sent the whole first cell
  as "authors", which polluted the query and produced false `MISMATCH` flags.
- Rows of any other table that carry a 4-digit year, by title alone.

The **Methodological Landscape** table (header starts with `Approach`) is
skipped. Its "Key Papers" column repeats titles in shorthand, usually cut off
with `...`, and those shorthand forms were the main source of false
`NOT_FOUND` flags. Independently of that, any quoted title ending in `...` or
`…`, or whose text is a prefix of a longer candidate, is dropped as a
truncated duplicate.

## When it runs

It runs automatically as an **advisory** step — it reports, and the command or
agent acts on the results; it never hard-blocks the workflow (Crossref or the
network can be flaky).

- `/wtfMS:literature-review` runs it on `.research/LITERATURE.md` before
  committing the review.
- `/wtfMS:execute-task` runs it on a completed task's `.bib` / reference output.

The response policy: nothing is removed automatically.

- **NOT_FOUND** → surface to the user with the closest Crossref result. The
  user decides whether to re-search and replace it, or keep it because it is
  a real work in a venue Crossref does not index (a preprint, a dataset, a
  thesis, a standards document).
- **MISMATCH** → surface to the user next to the Crossref match (title, year,
  DOI) so they can confirm it is the same work or correct the detail.
- **UNVERIFIABLE placeholder** → annotate as needing finalization before citing.

## Running it manually

```bash
# Verify a review (needs network for the Crossref lookups)
python3 wtf-ms/scripts/verify_citations.py .research/LITERATURE.md

# A task's references
python3 wtf-ms/scripts/verify_citations.py .research/tasks/task-01/*.bib

# Structural checks only, no network
python3 wtf-ms/scripts/verify_citations.py --offline .research/LITERATURE.md

# Machine-readable output
python3 wtf-ms/scripts/verify_citations.py --json .research/LITERATURE.md
```

Zero dependencies (Python stdlib only). Crossref needs no API key; requests
identify with a plain descriptive User-Agent. An HTTP 429 or 5xx response is
retried once after 2 s; if it fails again the entry is reported
`UNVERIFIABLE` (network error) rather than `NOT_FOUND`.

## How the behavior is tested

The extraction and classification logic is pinned by
`tests/test_verify_citations.py` (network-mocked, runs in CI). Those tests lock
in the tricky cases that were tuned by hand: quoted *emphasis phrases* in prose
must not be mistaken for titles, the Methodological Landscape table is
skipped, `...`-truncated and prefix duplicates are dropped, an author string
is derived only from a real author list, abbreviated titles (`"…in LPBF"`)
are rescued by author + year corroboration, compound surnames
(`Scipioni Bertoli`) match, a 404'd DOI is reported as fabricated rather than
as a network error, and a 429/5xx response is retried exactly once.

## Limitations

- Crossref covers most journals and conferences but not everything — a
  legitimate paper in an unindexed venue, preprint server, or book can come
  back `MISMATCH`/`NOT_FOUND`. Treat those as "verify by hand", not "delete".
- Verification confirms a paper *exists*; it does not confirm the paper
  *supports the claim* it is cited for. That judgment stays with the researcher.
