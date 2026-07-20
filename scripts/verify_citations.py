#!/usr/bin/env python3
"""
verify_citations — resolve the citations in wtf-MS research output against a
real bibliographic database (Crossref) to catch hallucinated / fabricated
references, the #1 failure mode of an LLM research assistant.

It reads LITERATURE.md and/or .bib files, extracts citation candidates
(BibTeX entries, and quoted paper titles from the "Key Papers" tables the
literature agent writes), then queries Crossref by DOI or by title+year and
classifies each candidate:

  VERIFIED      matched a real published work (title similar, year consistent)
  MISMATCH      a work was found but the metadata disagrees (wrong year, or
                only a weak title match) — possible fabrication or bad detail
  NOT_FOUND     no plausible match — likely hallucinated
  UNVERIFIABLE  no extractable title (e.g. a placeholder like "[ML disc. 2024]")

Design notes:
  * No DOIs are assumed — the literature agent usually emits none, so title+
    year resolution is the primary path.
  * Network is OPTIONAL. `--offline` (or a failed request) falls back to
    structural checks + placeholder detection so the tool still runs in CI or
    air-gapped sessions; unresolved entries become UNVERIFIABLE (offline).
  * Crossref is free and needs no key; we identify politely via User-Agent.

Exit status: non-zero if any NOT_FOUND or MISMATCH (a hallucination signal).
Zero deps (Python stdlib only).

Usage:
  python3 scripts/verify_citations.py .research/LITERATURE.md [more files ...]
  python3 scripts/verify_citations.py --offline path.bib
  python3 scripts/verify_citations.py --json .research/tasks/task-01/*.bib
"""
import argparse
import difflib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

CROSSREF = "https://api.crossref.org/works"
UA = "wtfms-verify-citations/0.1 (https://github.com/; mailto:wtfms@example.org)"
TITLE_MATCH = 0.75      # >= this title similarity => same paper
TITLE_WEAK = 0.50       # [WEAK, MATCH) => MISMATCH (found but doubtful)
REQ_TIMEOUT = 15
REQ_PAUSE = 0.2         # polite spacing between Crossref calls


# ---- extraction -----------------------------------------------------------

class Cite:
    __slots__ = ("title", "year", "authors", "doi", "source", "raw")

    def __init__(self, title=None, year=None, authors=None, doi=None,
                 source="", raw=""):
        self.title = title
        self.year = year
        self.authors = authors
        self.doi = doi
        self.source = source      # where in the file it came from
        self.raw = raw            # original text snippet


def _norm(s):
    """Lowercase, strip non-alphanumerics to single spaces — for comparison."""
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def similarity(a, b):
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def extract_bibtex(text, source):
    """Extract entries from a BibTeX blob."""
    cites = []
    for m in re.finditer(r"@\w+\s*\{([^,]*),(.*?)\n\}", text, re.DOTALL):
        body = m.group(2)

        def field(name):
            fm = re.search(name + r"\s*=\s*[{\"]([^}\"]*)[}\"]",
                           body, re.IGNORECASE)
            return fm.group(1).strip() if fm else None

        title = field("title")
        if not title:
            continue
        year = field("year")
        doi = field("doi")
        authors = field("author")
        cites.append(Cite(title=title, year=year, authors=authors, doi=doi,
                          source=source, raw=m.group(0)[:120]))
    return cites


# A quoted title: straight or curly quotes, reasonably long, containing a
# lowercase letter and a space (rules out short quoted phrases / acronyms).
_QUOTED = re.compile(r"[\"“]([^\"”“]{20,})[\"”]")

# An inline citation key like [Gong 2014] or [du Plessis 2019].
_INLINE = re.compile(r"\[([A-Za-z][\w.\- ]*?\s(?:19|20)\d{2}[a-z]?)\]")

# Placeholder-looking inline keys: contain a hyphenated/lowercase filler token
# rather than a proper surname (e.g. "ML domain-discovery 2024").
_PLACEHOLDER_HINT = re.compile(r"[a-z]+-[a-z]+|\b(?:ml|opt|disc|tbd|xxx)\b",
                               re.IGNORECASE)


def _is_bibliographic(line):
    """
    True if a line looks like a reference entry rather than prose. The
    literature agent puts full paper titles in the "Key Papers" markdown
    table (pipe rows) and cites by [Author Year] keys in prose, so a table
    row is the reliable signal. Prose lines — even those with emphasis
    italics (*single*) and a citation year — are excluded, which is what
    keeps quoted emphasis-phrases from being mistaken for titles.
    """
    return "|" in line


def extract_markdown(text, source):
    """
    Extract citation candidates from a LITERATURE.md-style document:
      * quoted paper titles found ONLY on bibliographic lines (table rows or
        italic-journal+year lines), with a nearby 4-digit year
      * inline [Author Year] keys (for placeholder / orphan detection)
    """
    cites = []
    seen_titles = set()
    for line in text.splitlines():
        if not _is_bibliographic(line):
            continue
        for qm in _QUOTED.finditer(line):
            title = qm.group(1).strip().rstrip(".")
            key = _norm(title)
            if key in seen_titles or len(key) < 12:
                continue
            seen_titles.add(key)
            ym = re.search(r"(?:19|20)\d{2}", line)
            year = ym.group(0) if ym else None
            # authors: leading text of the line before the first comma
            authors = line.split(",")[0].strip(" |*").strip() or None
            cites.append(Cite(title=title, year=year, authors=authors,
                              source=source, raw=line.strip()[:160]))
    return cites, _extract_inline(text, seen_titles, source)


def _surnames(authors):
    """
    Plausible primary-author surname tokens from a free-form author string.
    Author order is ambiguous here — tables use both "King W.E." (surname
    first) and "W.E. King" (surname last) — so we return every token that
    looks like a surname (capitalized, mostly letters) and drop initials
    like "W.E.". The caller matches this set against the work's authors.
    """
    if not authors:
        return set()
    first = re.split(r"\band\b|;|&", authors)[0]
    first = re.sub(r"\bet al\.?\b", "", first, flags=re.IGNORECASE)
    out = set()
    for tok in re.split(r"[\s,]+", first):
        letters = re.sub(r"[^A-Za-z]", "", tok)
        if len(letters) < 2:
            continue
        # An initials cluster like "W.E." -> "WE" is all-caps and short; skip.
        if tok.replace(".", "").isupper() and len(letters) <= 3:
            continue
        if tok[:1].isupper():
            out.add(_norm(letters))
    return out


def _item_surnames(item):
    """Normalized family names AND their word tokens (handles compound
    surnames like 'Scipioni Bertoli' whichever way the source split them)."""
    out = set()
    for a in (item.get("author") or []):
        fam = a.get("family")
        if not fam:
            continue
        nf = _norm(fam)
        out.add(nf)
        out.update(nf.split())
    return out


def _extract_inline(text, titled_norm, source):
    """Return placeholder-style inline keys that have no titled reference."""
    placeholders = []
    seen = set()
    for m in _INLINE.finditer(text):
        key = m.group(1).strip()
        if key in seen:
            continue
        seen.add(key)
        if _PLACEHOLDER_HINT.search(key):
            placeholders.append(Cite(title=None, source=source,
                                     raw="[" + key + "]"))
    return placeholders


# ---- verification ---------------------------------------------------------

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as r:
        return json.load(r)


DOI_ABSENT = object()   # sentinel: DOI definitively not in Crossref (HTTP 404)


def crossref_by_doi(doi):
    """Return the work dict, DOI_ABSENT if Crossref 404s (fabricated DOI),
    or None on a real network error."""
    try:
        data = _get(CROSSREF + "/" + urllib.parse.quote(doi))
        return data.get("message")
    except urllib.error.HTTPError as e:
        return DOI_ABSENT if e.code == 404 else None
    except Exception:
        return None


def crossref_by_title(title, authors=None, year=None):
    q = title
    if authors:
        q = authors + " " + q
    params = {"rows": "5", "query.bibliographic": q}
    url = CROSSREF + "?" + urllib.parse.urlencode(params)
    try:
        data = _get(url)
        return data.get("message", {}).get("items", [])
    except Exception:
        return None      # None = network failure (vs [] = no results)


def _item_year(item):
    for k in ("published-print", "published-online", "issued"):
        dp = item.get(k, {}).get("date-parts") if item else None
        if dp and dp[0] and dp[0][0]:
            return str(dp[0][0])
    return None


def verify_one(c, offline):
    """Return (status, detail_dict)."""
    if not c.title:
        return "UNVERIFIABLE", {"reason": "no extractable title (placeholder)"}
    if offline:
        return "UNVERIFIABLE", {"reason": "offline mode — not resolved"}

    # DOI path
    if c.doi:
        item = crossref_by_doi(c.doi)
        if item is DOI_ABSENT:
            return "NOT_FOUND", {"doi": c.doi,
                                 "reason": "DOI does not exist in Crossref"}
        if item is None:
            return "UNVERIFIABLE", {"reason": "network error resolving DOI"}
        rt = (item.get("title") or [""])[0]
        sim = similarity(c.title, rt)
        if sim >= TITLE_WEAK:
            return "VERIFIED", {"doi": c.doi, "matched_title": rt,
                                "similarity": round(sim, 2)}
        return "MISMATCH", {"doi": c.doi, "matched_title": rt,
                            "similarity": round(sim, 2),
                            "reason": "DOI resolves to a different title"}

    # Title path
    items = crossref_by_title(c.title, c.authors, c.year)
    if items is None:
        return "UNVERIFIABLE", {"reason": "network error querying Crossref"}
    best, best_sim = None, 0.0
    for it in items:
        rt = (it.get("title") or [""])[0]
        s = similarity(c.title, rt)
        if s > best_sim:
            best, best_sim = it, s
    if best is None:
        return "NOT_FOUND", {"reason": "no Crossref results"}
    rt = (best.get("title") or [""])[0]
    ry = _item_year(best)
    detail = {"matched_title": rt, "similarity": round(best_sim, 2),
              "doi": best.get("DOI"), "matched_year": ry}

    year_ok = not (c.year and ry) or abs(int(c.year) - int(ry)) <= 1
    # Author+year corroboration rescues abbreviated titles (e.g. a source
    # that shortened "...laser powder-bed fusion" to "...LPBF"): the primary
    # author's surname appearing in the matched work, with a consistent year,
    # is strong independent evidence it is the same paper.
    author_ok = bool(_surnames(c.authors) & _item_surnames(best))

    if best_sim >= TITLE_MATCH:
        if not year_ok:
            detail["reason"] = f"year {c.year} vs Crossref {ry}"
            return "MISMATCH", detail
        return "VERIFIED", detail
    if best_sim >= TITLE_WEAK:
        if author_ok and year_ok:
            detail["reason"] = "abbreviated title; confirmed by author + year"
            return "VERIFIED", detail
        detail["reason"] = "only a weak title match — verify manually"
        return "MISMATCH", detail
    detail["reason"] = "closest Crossref result is unrelated"
    return "NOT_FOUND", detail


# ---- driver ---------------------------------------------------------------

def collect(paths):
    cites, placeholders = [], []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"WARN: cannot read {p}: {e}", file=sys.stderr)
            continue
        if p.endswith(".bib"):
            cites += extract_bibtex(text, p)
        else:
            md_cites, md_ph = extract_markdown(text, p)
            cites += md_cites
            placeholders += md_ph
    return cites, placeholders


def main():
    ap = argparse.ArgumentParser(description="Verify citations against Crossref.")
    ap.add_argument("paths", nargs="+", help="LITERATURE.md and/or .bib files")
    ap.add_argument("--offline", action="store_true",
                    help="skip network; structural + placeholder checks only")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    cites, placeholders = collect(args.paths)

    results = []
    for c in cites:
        status, detail = verify_one(c, args.offline)
        results.append((c, status, detail))
        if not args.offline and not c.doi:
            time.sleep(REQ_PAUSE)
    for ph in placeholders:
        results.append((ph, "UNVERIFIABLE",
                        {"reason": "self-flagged placeholder citation key"}))

    counts = {}
    for _, status, _ in results:
        counts[status] = counts.get(status, 0) + 1

    if args.json:
        out = {
            "summary": counts,
            "results": [
                {"title": c.title, "year": c.year, "doi": c.doi,
                 "source": c.source, "raw": c.raw,
                 "status": status, "detail": detail}
                for c, status, detail in results
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        _print_report(results, counts, args.offline)

    bad = counts.get("NOT_FOUND", 0) + counts.get("MISMATCH", 0)
    return 1 if bad else 0


_ICON = {"VERIFIED": "OK  ", "MISMATCH": "WARN", "NOT_FOUND": "FAIL",
         "UNVERIFIABLE": "??  "}


def _print_report(results, counts, offline):
    order = ["NOT_FOUND", "MISMATCH", "UNVERIFIABLE", "VERIFIED"]
    for status in order:
        group = [(c, d) for c, s, d in results if s == status]
        if not group:
            continue
        print(f"\n{status} ({len(group)}):")
        for c, d in group:
            label = c.title or c.raw or "?"
            line = f"  [{_ICON[status]}] {label[:88]}"
            print(line)
            bits = []
            if d.get("reason"):
                bits.append(d["reason"])
            if d.get("matched_title") and status != "NOT_FOUND":
                bits.append(f"~ {d['matched_title'][:70]}")
            if d.get("doi") and status in ("VERIFIED", "MISMATCH"):
                bits.append(f"doi:{d['doi']}")
            if bits:
                print("           " + " | ".join(bits))
    mode = " (offline)" if offline else ""
    print(f"\nverify-citations{mode}: " +
          ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "no citations found")
    bad = counts.get("NOT_FOUND", 0) + counts.get("MISMATCH", 0)
    if bad:
        print(f"  -> {bad} citation(s) need attention.")


if __name__ == "__main__":
    sys.exit(main())
