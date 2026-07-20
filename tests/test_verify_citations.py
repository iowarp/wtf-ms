#!/usr/bin/env python3
"""
Unit tests for the citation verifier. No network — Crossref lookups are
monkeypatched — so these run deterministically in CI and lock in the
extraction/classification precision the tool was tuned for.

Run:  python3 tests/test_verify_citations.py     (or: python3 -m unittest)
"""
import importlib.util
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_MOD = os.path.join(_HERE, "..", ".claude", "wtf-ms", "scripts",
                    "verify_citations.py")
_spec = importlib.util.spec_from_file_location("verify_citations", _MOD)
vc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vc)


def item(title, year=None, doi="10.0/x", families=()):
    d = {"title": [title], "DOI": doi,
         "author": [{"family": f} for f in families]}
    if year:
        d["issued"] = {"date-parts": [[year]]}
    return d


class TestExtraction(unittest.TestCase):
    def test_table_row_title_extracted(self):
        md = ('## Key Papers\n'
              '| Tang M., Pistorius P.C., *Additive Manufacturing* 14 — '
              '"Prediction of lack-of-fusion porosity for powder bed fusion" '
              '| 2017 | key |\n')
        cites, _ = vc.extract_markdown(md, "x.md")
        self.assertEqual(len(cites), 1)
        self.assertIn("lack-of-fusion", cites[0].title)
        self.assertEqual(cites[0].year, "2017")

    def test_prose_emphasis_not_extracted(self):
        # Quoted emphasis + a citation year + a markdown italic, but no table:
        # must NOT be treated as a paper title.
        md = ('VED as a *single* design parameter was shown to "fail to '
              'capture melt-pool physics" by several groups in 2017.\n')
        cites, _ = vc.extract_markdown(md, "x.md")
        self.assertEqual(cites, [])

    def test_placeholder_inline_key_detected(self):
        md = "Recent work [ML domain-discovery 2024] confirms interest.\n"
        _, placeholders = vc.extract_markdown(md, "x.md")
        self.assertEqual(len(placeholders), 1)

    def test_bibtex_extraction(self):
        bib = ('@article{k, title={A Real Title Here}, author={Doe, Jane}, '
               'year={2020}, doi={10.1/abc}\n}\n')
        cites = vc.extract_bibtex(bib, "r.bib")
        self.assertEqual(len(cites), 1)
        self.assertEqual(cites[0].doi, "10.1/abc")


class TestSurnames(unittest.TestCase):
    def test_surname_first_format(self):
        self.assertIn("king", vc._surnames("King W.E. et al."))

    def test_surname_last_format(self):
        self.assertIn("king", vc._surnames("W.E. King and R. Smith"))

    def test_compound_surname(self):
        s = vc._surnames("Scipioni Bertoli U. et al.")
        self.assertIn("scipioni", s)
        self.assertIn("bertoli", s)

    def test_item_surnames_tokenizes_compound(self):
        it = item("t", families=["Scipioni Bertoli"])
        surns = vc._item_surnames(it)
        self.assertIn("scipioni", surns)
        self.assertIn("bertoli", surns)


class TestClassification(unittest.TestCase):
    def _title(self, c, patch_items):
        vc.crossref_by_title = lambda *a, **k: patch_items
        return vc.verify_one(c, offline=False)

    def test_verified_exact(self):
        c = vc.Cite(title="Prediction of lack-of-fusion porosity for PBF",
                    year="2017")
        status, _ = self._title(c, [item(
            "Prediction of lack-of-fusion porosity for PBF", 2017)])
        self.assertEqual(status, "VERIFIED")

    def test_mismatch_by_year(self):
        c = vc.Cite(title="A study of grain growth in nickel alloys",
                    year="2010")
        status, d = self._title(c, [item(
            "A study of grain growth in nickel alloys", 2024)])
        self.assertEqual(status, "MISMATCH")
        self.assertIn("year", d["reason"])

    def test_not_found(self):
        c = vc.Cite(title="A totally unique fabricated paper title xyzzy")
        status, _ = self._title(c, [item("Something completely different")])
        self.assertEqual(status, "NOT_FOUND")

    def test_abbreviated_title_rescued_by_author_year(self):
        # Weak title similarity, but author surname + year corroborate.
        c = vc.Cite(
            title="Observation of keyhole-mode laser melting in LPBF",
            year="2014", authors="King W.E. et al.")
        matched = item(
            "Observation of keyhole-mode laser melting in laser "
            "powder-bed fusion additive manufacturing systems",
            2014, families=["King"])
        status, d = self._title(c, [matched])
        self.assertEqual(status, "VERIFIED")
        self.assertIn("author", d["reason"])

    def test_no_results_not_found(self):
        c = vc.Cite(title="Anything at all here")
        status, _ = self._title(c, [])
        self.assertEqual(status, "NOT_FOUND")

    def test_network_error_unverifiable(self):
        c = vc.Cite(title="Anything at all here")
        vc.crossref_by_title = lambda *a, **k: None   # None == network failure
        status, _ = vc.verify_one(c, offline=False)
        self.assertEqual(status, "UNVERIFIABLE")

    def test_dead_doi_is_not_found(self):
        c = vc.Cite(title="Paper with a fabricated DOI", doi="10.9/fake")
        vc.crossref_by_doi = lambda doi: vc.DOI_ABSENT
        status, d = vc.verify_one(c, offline=False)
        self.assertEqual(status, "NOT_FOUND")
        self.assertIn("does not exist", d["reason"])

    def test_offline_is_unverifiable(self):
        c = vc.Cite(title="Any title", doi="10.1/x")
        status, _ = vc.verify_one(c, offline=True)
        self.assertEqual(status, "UNVERIFIABLE")

    def test_no_title_is_unverifiable(self):
        c = vc.Cite(title=None)
        status, _ = vc.verify_one(c, offline=False)
        self.assertEqual(status, "UNVERIFIABLE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
