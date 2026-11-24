"""Tests for the reference pairs and for the format checker.

Two things are tested here:

1. The checker accepts the published file and rejects broken ones.
2. Every reference answer in the file is recomputed from the formula in its
   cited source, with exact fractions and 40-digit decimals from the Python
   standard library. No units library and no tool under test is involved.

Run: python3 -m unittest discover -s tests -v
Written by Claude (AI).
"""
import copy
import json
import os
import sys
import unittest
from decimal import Decimal, getcontext
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_pairs  # noqa: E402

getcontext().prec = 40


def load():
    with open(os.path.join(ROOT, "pairs", "pairs.json"), encoding="utf-8") as handle:
        return json.load(handle)


def sqrt(fraction):
    """Square root of an exact fraction, to 40 significant digits."""
    return (Decimal(fraction.numerator) / Decimal(fraction.denominator)).sqrt()


def recompute():
    """Reference answers recomputed from the cited formulas, by pair id."""
    readings = [F("10.1"), F("10.3"), F("10.2"), F("10.4"), F("10.0")]
    n = len(readings)
    mean = sum(readings) / n
    return {
        # NIST SP 811 B.8: 1 in = 0.0254 m exactly.
        "conv-inch-mm": {"value": 1 * F("0.0254") * 1000},
        # NIST SP 811 footnote 22: 1 lb = 0.45359237 kg exactly.
        "conv-pound-kg": {"value": 150 * F("0.45359237")},
        # 1 km = 1000 m, 1 h = 3600 s.
        "conv-kmh-ms": {"value": 90 * F(1000, 3600)},
        # NIST SP 811 B.8: 1 kW.h = 3.6e6 J exactly.
        "conv-kwh-j": {"value": F("2.5") * 3600000},
        # NIST SP 811 B.8: T/K = t/degC + 273.15.
        "conv-degc-k": {"value": 25 + F("273.15")},
        # NIST SP 811 B.8: t/degC = (t/degF - 32)/1.8.
        "conv-degf-degc": {"value": (F("98.6") - 32) / F("1.8")},
        # NIST TN 1297 (A-4), (A-5).
        "typea-mean-five-readings": {
            "mean": mean,
            "standard_uncertainty": sqrt(sum((r - mean) ** 2 for r in readings) / (n * (n - 1))),
        },
        # NIST TN 1297 4.6: u = a/sqrt(3).
        "typeb-rectangular-half-width": {
            "standard_uncertainty": sqrt(F("0.05") ** 2 / 3),
        },
        # NIST TN 1297 (A-3), P = V*I, no covariance.
        "comb-product-uncorrelated": {
            "value": F("10.0") * F("2.00"),
            "combined_standard_uncertainty": sqrt(
                (F("2.00") * F("0.1")) ** 2 + (F("10.0") * F("0.04")) ** 2),
        },
        # NIST TN 1297 (A-3), L = x1 + x2, with covariance.
        "comb-sum-with-covariance": {
            "value": F("50.000") + F("30.000"),
            "combined_standard_uncertainty": sqrt(
                F("0.003") ** 2 + F("0.004") ** 2 + 2 * F("0.000012")),
        },
    }


def as_decimal(number):
    if isinstance(number, Decimal):
        return number
    return Decimal(number.numerator) / Decimal(number.denominator)


class PublishedFile(unittest.TestCase):
    def test_file_is_valid(self):
        self.assertEqual(check_pairs.check_document(load()), [])

    def test_every_pair_is_recomputed(self):
        ids = {pair["id"] for pair in load()["pairs"]
               if pair["reference"].get("outcome") != "refuse"}
        self.assertEqual(ids, set(recompute()))

    def test_refuse_pairs_have_units_of_different_dimension(self):
        """Dimensions written out by hand here, not taken from any units tool."""
        dimension = {"m": "L", "s": "T"}
        refuse = [p for p in load()["pairs"] if p["reference"].get("outcome") == "refuse"]
        self.assertTrue(refuse)
        for pair in refuse:
            with self.subTest(pair=pair["id"]):
                self.assertEqual(pair["task"], "add")
                dims = {dimension[t["unit"]] for t in pair["inputs"]["terms"]}
                self.assertGreater(len(dims), 1)

    def test_reference_answers_match_recomputation(self):
        expected = recompute()
        for pair in load()["pairs"]:
            for out in pair["reference"].get("outputs", []):
                with self.subTest(pair=pair["id"], output=out["name"]):
                    ours = as_decimal(expected[pair["id"]][out["name"]])
                    stated = as_decimal(check_pairs.parse_number(out["value"]))
                    if out["exact"]:
                        # Exact answers must match to all 40 working digits.
                        self.assertLessEqual(abs(ours - stated), abs(ours) * Decimal("1e-38"))
                    else:
                        # Rounded answers are written to 12 significant digits.
                        self.assertLessEqual(abs(ours - stated), abs(ours) * Decimal("5e-12"))

    def test_rounding_error_is_inside_tolerance(self):
        """A rounded reference must be much more precise than its tolerance."""
        for pair in load()["pairs"]:
            for out in pair["reference"].get("outputs", []):
                if out["exact"]:
                    continue
                with self.subTest(pair=pair["id"], output=out["name"]):
                    self.assertEqual(out["tolerance"]["kind"], "relative")
                    tol = as_decimal(check_pairs.parse_number(out["tolerance"]["value"]))
                    self.assertGreaterEqual(tol, Decimal("1e-10"))

    def test_first_step_has_ten_pairs(self):
        self.assertGreaterEqual(len(load()["pairs"]), 10)


class CheckerRejectsBrokenFiles(unittest.TestCase):
    def broken(self, change):
        doc = copy.deepcopy(load())
        change(doc)
        return check_pairs.check_document(doc)

    def test_missing_source(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][0].update(sources=[])))

    def test_source_without_locator(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][0]["sources"][0].pop("locator")))

    def test_duplicate_id(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][1].update(id=d["pairs"][0]["id"])))

    def test_number_not_a_string(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][0]["inputs"].update(value=1.0)))

    def test_missing_tolerance(self):
        self.assertTrue(self.broken(
            lambda d: d["pairs"][0]["reference"]["outputs"][0].pop("tolerance")))

    def test_wrong_output_names(self):
        self.assertTrue(self.broken(
            lambda d: d["pairs"][6]["reference"]["outputs"].pop()))

    def test_unknown_task(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][0].update(task="guess")))

    def test_impossible_covariance(self):
        self.assertTrue(self.broken(
            lambda d: d["pairs"][9]["inputs"]["covariances"][0].update(value="0.001")))

    def test_missing_derivation(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][0].pop("derivation")))

    def test_unknown_outcome(self):
        self.assertTrue(self.broken(
            lambda d: d["pairs"][0].update(reference={"outcome": "maybe"})))

    def test_add_needs_two_terms(self):
        self.assertTrue(self.broken(
            lambda d: d["pairs"][-1]["inputs"]["terms"].pop()))

    def test_wrong_format_version(self):
        self.assertTrue(self.broken(lambda d: d.update(format_version=2)))

    def test_refuse_reference_is_accepted(self):
        self.assertEqual(self.broken(
            lambda d: d["pairs"][0].update(reference={"outcome": "refuse"})), [])


class NumberParsing(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(check_pairs.parse_number("25.4"), F(254, 10))
        self.assertEqual(check_pairs.parse_number("250/9"), F(250, 9))
        self.assertEqual(check_pairs.parse_number("1e-9"), F(1, 10 ** 9))
        with self.assertRaises(ValueError):
            check_pairs.parse_number(25.4)


if __name__ == "__main__":
    unittest.main()
