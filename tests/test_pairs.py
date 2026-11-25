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


def by_id(doc, pair_id):
    return next(p for p in doc["pairs"] if p["id"] == pair_id)


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
        # NIST SP 811 B.8, exact factors (bold in the table).
        "conv-foot-m": {"value": 6 * F("0.3048")},
        "conv-mile-km": {"value": F("26.2") * F("1609.344") / 1000},
        "conv-mph-ms": {"value": 60 * F("0.44704")},
        "conv-nautical-mile-km": {"value": 10 * F(1852) / 1000},
        "conv-litre-m3": {"value": 250 * F("0.001")},
        "conv-atm-kpa": {"value": 1 * F(101325) / 1000},
        "conv-bar-pa": {"value": F("2.5") * 100000},
        "conv-calth-j": {"value": 500 * F("4.184")},
        "conv-sqin-mm2": {"value": 2 * F("0.00064516") * 1000000},
        # NIST SP 811 B.8: T/K = (t/degF + 459.67)/1.8.
        "conv-degf-k": {"value": (F(-40) + F("459.67")) / F("1.8")},
        # 1 min = 60 s, 1 h = 3600 s.
        "conv-min-h": {"value": 90 * F(60) / 3600},
        # 1 ft = 0.3048 m, 1 in = 0.0254 m.
        "dim-add-foot-inch": {"value": F("0.3048") + 6 * F("0.0254")},
        # NIST TN 1297 (A-3), R = V/I: c_V = 1/I, c_I = -V/I^2.
        "comb-quotient-uncorrelated": {
            "value": F("12.0") / F("3.00"),
            "combined_standard_uncertainty": sqrt(
                (F("0.06") / F("3.00")) ** 2
                + (F("12.0") / F("3.00") ** 2 * F("0.03")) ** 2),
        },
        # (A-3), d = x1 - x2: c = 1, -1, so the covariance term is negative.
        "comb-difference-with-covariance": {
            "value": F("100.000") - F("40.000"),
            "combined_standard_uncertainty": sqrt(
                F("0.005") ** 2 + F("0.005") ** 2 - 2 * F("0.000016")),
        },
        # (A-3) with one input: A = s^2, c = 2s.
        "comb-square-same-variable": {
            "value": F("2.000") ** 2,
            "combined_standard_uncertainty": 2 * F("2.000") * F("0.010"),
        },
        # (A-3) with one input, written as a power: A = s^2, c = 2s.
        "comb-square-as-power": {
            "value": F("3.000") ** 2,
            "combined_standard_uncertainty": 2 * F("3.000") * F("0.020"),
        },
        # (A-3), P = V*I with V given in millivolts: 5000 mV = 5 V, 20 mV = 0.02 V.
        "comb-product-mixed-units": {
            "value": F(5000) / 1000 * F("0.4"),
            "combined_standard_uncertainty": sqrt(
                (F("0.4") * F(20) / 1000) ** 2 + (F(5000) / 1000 * F("0.002")) ** 2),
        },
        # (A-3), y = 2a + 3b.
        "comb-linear-combination": {
            "value": 2 * F("1.0") + 3 * F("2.0"),
            "combined_standard_uncertainty": sqrt(
                (2 * F("0.1")) ** 2 + (3 * F("0.2")) ** 2),
        },
        # NIST TN 1297 (A-4), (A-5).
        "typea-mean-four-readings": _type_a(["5.01", "5.03", "4.98", "5.02"]),
        # NIST TN 1297 4.6: u = a/sqrt(6).
        "typeb-triangular-half-width": {
            "standard_uncertainty": sqrt(F("0.06") ** 2 / 6),
        },
        # NIST SP 811 B.8: an interval in degF is divided by 1.8, with no offset.
        "conv-degf-interval-k": {"value": 9 / F("1.8")},
        # NIST SP 811 8.5: an interval has the same numerical value in degC and in K.
        "conv-degc-interval-k": {"value": F(15)},
        # NIST TN 1297 4.6: normal, limits containing about 99.73 percent: u = a/3.
        "typeb-normal-9973-limits": {"standard_uncertainty": F("0.6") / 3},
        # NIST TN 1297 4.3: a 95 percent confidence interval is divided by 1.960.
        "typeb-normal-95-interval": {"standard_uncertainty": F("0.0392") / F("1.960")},
        # NIST TN 1297 (B-1), Welch-Satterthwaite.
        "dof-welch-satterthwaite-two": {
            "effective_degrees_of_freedom": _welch_satterthwaite([("0.3", 4), ("0.4", 9)]),
        },
        "dof-welch-satterthwaite-three": {
            "effective_degrees_of_freedom": _welch_satterthwaite(
                [("1.0", 5), ("2.0", 10), ("2.0", 20)]),
        },
        # NIST SP 811 B.7.1, the three rounding rules.
        "round-half-odd-goes-up": {"value": _round_sp811("2.675", 3)},
        "round-half-even-stays": {"value": _round_sp811("2.665", 3)},
        "round-above-half-goes-up": {"value": _round_sp811("1.2501", 2)},
    }


def _welch_satterthwaite(components):
    """nu_eff = (sum u_i^2)^2 / sum(u_i^4 / nu_i), exactly."""
    numerator = sum(F(u) ** 2 for u, nu in components) ** 2
    return numerator / sum(F(u) ** 4 / nu for u, nu in components)


def _round_sp811(text, digits):
    """Round a positive decimal string to `digits` significant digits by the
    three rules of NIST SP 811 B.7.1, working on the digits themselves."""
    whole, _, fraction = text.partition(".")
    all_digits = (whole + fraction).lstrip("0")
    leading_zeros = len(whole + fraction) - len(all_digits)
    kept, dropped = all_digits[:digits], all_digits[digits:]
    number = int(kept)
    if dropped and dropped[0] > "5":
        number += 1                                   # more than half: up
    elif dropped and dropped[0] == "5":
        if dropped[1:].strip("0"):
            number += 1                               # rule 2: 5 followed by non-zero
        elif number % 2 == 1:
            number += 1                               # rule 3: exactly 5, make even
    # rule 1 (first dropped digit below 5): unchanged
    exponent = len(whole) - leading_zeros - digits    # power of ten of the last kept digit
    return F(number) * F(10) ** exponent


def _type_a(readings):
    values = [F(r) for r in readings]
    n = len(values)
    mean = sum(values) / n
    return {
        "mean": mean,
        "standard_uncertainty": sqrt(sum((v - mean) ** 2 for v in values) / (n * (n - 1))),
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
        dimension = {"m": "L", "s": "T", "kg": "M", "V": "M L2 T-3 I-1", "A": "I"}
        refuse = [p for p in load()["pairs"] if p["reference"].get("outcome") == "refuse"]
        self.assertTrue(refuse)
        for pair in refuse:
            with self.subTest(pair=pair["id"]):
                self.assertIn(pair["task"], ("add", "convert"))
                if pair["task"] == "add":
                    units = [t["unit"] for t in pair["inputs"]["terms"]]
                else:
                    units = [pair["inputs"]["unit"], pair["inputs"]["to_unit"]]
                dims = {dimension[unit] for unit in units}
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

    def test_first_release_has_thirty_pairs(self):
        self.assertGreaterEqual(len(load()["pairs"]), 30)

    def test_same_kind_sums_are_not_marked_refuse(self):
        """The control pair: a sum of two lengths has an answer."""
        pair = by_id(load(), "dim-add-foot-inch")
        self.assertNotIn("outcome", pair["reference"])


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
            lambda d: by_id(d, "typea-mean-five-readings")["reference"]["outputs"].pop()))

    def test_unknown_task(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][0].update(task="guess")))

    def test_impossible_covariance(self):
        self.assertTrue(self.broken(
            lambda d: by_id(d, "comb-sum-with-covariance")["inputs"]["covariances"][0].update(value="0.001")))

    def test_missing_derivation(self):
        self.assertTrue(self.broken(lambda d: d["pairs"][0].pop("derivation")))

    def test_unknown_outcome(self):
        self.assertTrue(self.broken(
            lambda d: d["pairs"][0].update(reference={"outcome": "maybe"})))

    def test_add_needs_two_terms(self):
        self.assertTrue(self.broken(
            lambda d: by_id(d, "dim-add-length-time")["inputs"]["terms"].pop()))

    def test_wrong_format_version(self):
        self.assertTrue(self.broken(lambda d: d.update(format_version=3)))

    def test_refuse_reference_is_accepted(self):
        self.assertEqual(self.broken(
            lambda d: d["pairs"][0].update(reference={"outcome": "refuse"})), [])


class ProposedVersionTwo(unittest.TestCase):
    """The proposal in FORMAT.md, with its example file pairs/proposed-v2.json."""

    PATH = os.path.join(ROOT, "pairs", "proposed-v2.json")

    def doc(self):
        with open(self.PATH, encoding="utf-8") as handle:
            return json.load(handle)

    def broken(self, change):
        doc = self.doc()
        change(doc)
        return check_pairs.check_document(doc)

    def item(self, doc, pid):
        return next(p for p in doc["pairs"] if p["id"] == pid)

    def test_example_file_is_valid(self):
        self.assertEqual(check_pairs.check_document(self.doc()), [])

    def test_published_pairs_stay_at_version_one(self):
        self.assertEqual(load()["format_version"], 1)

    def test_new_things_are_refused_under_version_one(self):
        for pid in ("amb-calorie-joule", "lab-inch-mm-states-unit", "rel-inch-mm-round-trip"):
            doc = self.doc()
            doc["format_version"] = 1
            doc["pairs"] = [self.item(doc, pid)]
            self.assertTrue(check_pairs.check_document(doc), pid)

    def test_any_of_needs_two_answers(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "amb-calorie-joule")["reference"]["answers"].pop()))

    def test_any_of_must_say_whether_a_refusal_passes(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "amb-calorie-joule")["reference"].pop("refusal_passes")))

    def test_any_of_answer_needs_stated_as(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "amb-calorie-joule")["reference"]["answers"][0].pop("stated_as")))

    def test_any_of_answers_are_recomputed(self):
        """Both readings follow from the factors in the source: 1 x factor."""
        answers = self.item(self.doc(), "amb-calorie-joule")["reference"]["answers"]
        values = sorted(F(a["outputs"][0]["value"]) for a in answers)
        self.assertEqual(values, [F("4.184"), F("4.1868")])

    def test_unknown_label(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "lab-inch-mm-states-unit")["reference"]["must_state"][0]
            .update(what="colour")))

    def test_relation_cannot_use_a_later_call(self):
        def change(d):
            calls = self.item(d, "rel-inch-mm-round-trip")["calls"]
            calls.reverse()
        self.assertTrue(self.broken(change))

    def test_relation_cannot_use_an_unknown_output(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "rel-square-two-ways")["relation"].update(left="product.area")))

    def test_relation_expression_is_arithmetic_only(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "rel-inch-mm-round-trip")["relation"]
            .update(left="__import__('os').getcwd()")))

    def test_relation_needs_a_tolerance(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "rel-inch-mm-round-trip")["relation"].pop("tolerance")))

    def test_relation_needs_a_source(self):
        self.assertTrue(self.broken(
            lambda d: self.item(d, "rel-square-two-ways").update(sources=[])))

    def test_round_trip_holds_in_exact_arithmetic(self):
        self.assertEqual(F(7) * F("25.4") / F("25.4"), 7)

    def test_optional_accuracy_fields(self):
        def add(d):
            out = self.item(d, "lab-inch-mm-states-unit")["reference"]["outputs"][0]
            out.update(reference_accuracy="0", sensitivity="1")
        self.assertEqual(self.broken(add), [])
        self.assertTrue(self.broken(
            lambda d: self.item(d, "lab-inch-mm-states-unit")["reference"]["outputs"][0]
            .update(sensitivity="0.5")))

    def test_expression_references(self):
        self.assertEqual(check_pairs.expression_references("b.value - 2 * a.value"),
                         [("b", "value"), ("a", "value")])
        with self.assertRaises(ValueError):
            check_pairs.expression_references("open('x')")


class RoundingHelper(unittest.TestCase):
    """The helper is checked against the worked examples printed in NIST SP 811 B.7.1."""

    def test_examples_from_the_source(self):
        for text, digits, expected in [
            ("6.9749515", 3, "6.97"),
            ("6.9749515", 2, "7.0"),
            ("6.9749515", 5, "6.9750"),
            ("6.9749515", 7, "6.974952"),
            ("6.9749505", 7, "6.974950"),
        ]:
            with self.subTest(value=text, digits=digits):
                self.assertEqual(_round_sp811(text, digits), F(expected))

    def test_small_and_large_numbers(self):
        self.assertEqual(_round_sp811("0.0125", 2), F("0.012"))
        self.assertEqual(_round_sp811("1250", 2), F(1200))
        self.assertEqual(_round_sp811("1350", 2), F(1400))


class CheckerNewTasks(unittest.TestCase):
    def broken(self, pair_id, change):
        doc = copy.deepcopy(load())
        change(next(p for p in doc["pairs"] if p["id"] == pair_id))
        return check_pairs.check_document(doc)

    def test_normal_needs_a_coverage_probability(self):
        self.assertTrue(self.broken("typeb-normal-95-interval",
                                    lambda p: p["inputs"].pop("coverage_probability")))
        self.assertTrue(self.broken("typeb-normal-95-interval",
                                    lambda p: p["inputs"].update(coverage_probability="1.5")))

    def test_dof_components(self):
        self.assertTrue(self.broken("dof-welch-satterthwaite-two",
                                    lambda p: p["inputs"]["components"].pop()))
        self.assertTrue(self.broken(
            "dof-welch-satterthwaite-two",
            lambda p: p["inputs"]["components"][0].update(degrees_of_freedom="0")))

    def test_round_needs_whole_digits(self):
        self.assertTrue(self.broken("round-half-even-stays",
                                    lambda p: p["inputs"].update(significant_digits="3")))
        self.assertTrue(self.broken("round-half-even-stays",
                                    lambda p: p["inputs"].update(significant_digits=0)))


class NumberParsing(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(check_pairs.parse_number("25.4"), F(254, 10))
        self.assertEqual(check_pairs.parse_number("250/9"), F(250, 9))
        self.assertEqual(check_pairs.parse_number("1e-9"), F(1, 10 ** 9))
        with self.assertRaises(ValueError):
            check_pairs.parse_number(25.4)


if __name__ == "__main__":
    unittest.main()
