"""Tests for the runner itself, using made-up adapters with known behaviour.

Run: python3 -m unittest discover -s tests -v
Written by Claude (AI).
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from bench import model, runner  # noqa: E402
from bench.runner import Answer, Refusal, Unsupported  # noqa: E402

PAIRS = runner.load_pairs(os.path.join(ROOT, "pairs", "pairs.json"))
BY_ID = {pair["id"]: pair for pair in PAIRS}


class Fake:
    """An adapter whose answer for every pair is given by a function."""
    name = "fake"

    def __init__(self, solve):
        self.solve = solve

    def versions(self):
        return {"fake": "0"}


def echo(pair):
    """Answers every pair with its own reference: the perfect tool."""
    if pair["reference"].get("outcome") == "refuse":
        return Refusal("no")
    return Answer({o["name"]: float(runner.Fraction(o["value"]))
                   for o in pair["reference"]["outputs"]})


def numeric_output(value, tolerance="1e-9", kind="relative"):
    return {"name": "value", "value": value, "unit": "x", "exact": True,
            "tolerance": {"kind": kind, "value": tolerance}}


class Compare(unittest.TestCase):
    def test_inside_and_outside_relative_tolerance(self):
        out = numeric_output("100", "1e-3")
        self.assertTrue(runner.compare(out, 100.09)[0])
        self.assertFalse(runner.compare(out, 100.11)[0])
        self.assertFalse(runner.compare(out, 99.89)[0])

    def test_boundary_counts_as_pass(self):
        out = numeric_output("100", "0.25")
        self.assertTrue(runner.compare(out, 125.0)[0])
        self.assertTrue(runner.compare(out, 75.0)[0])

    def test_absolute_tolerance(self):
        out = numeric_output("0", "0.5", kind="absolute")
        ok, difference, relative = runner.compare(out, 0.25)
        self.assertTrue(ok)
        self.assertEqual(difference, 0.25)
        self.assertIsNone(relative)  # no relative difference from zero
        self.assertFalse(runner.compare(out, -0.75)[0])

    def test_negative_reference(self):
        out = numeric_output("-40", "1e-6")
        self.assertTrue(runner.compare(out, -40.00001)[0])
        self.assertFalse(runner.compare(out, 40.0)[0])

    def test_nan_and_infinity_fail(self):
        out = numeric_output("1")
        self.assertFalse(runner.compare(out, float("nan"))[0])
        self.assertFalse(runner.compare(out, float("inf"))[0])

    def test_non_numbers_are_rejected(self):
        out = numeric_output("1")
        for bad in ("1", None, True, [1.0]):
            with self.assertRaises(TypeError):
                runner.compare(out, bad)

    def test_difference_is_reported(self):
        ok, difference, relative = runner.compare(numeric_output("200", "1e-9"), 201.0)
        self.assertFalse(ok)
        self.assertEqual(difference, 1.0)
        self.assertEqual(relative, 0.005)


class Judge(unittest.TestCase):
    def verdict(self, pair_id, answer):
        return runner.judge(BY_ID[pair_id], answer)["verdict"]

    def test_right_answer_passes(self):
        self.assertEqual(self.verdict("conv-inch-mm", Answer({"value": 25.4})), "pass")

    def test_wrong_answer_fails(self):
        self.assertEqual(self.verdict("conv-inch-mm", Answer({"value": 25.5})), "fail")

    def test_one_wrong_output_of_two_fails(self):
        answer = Answer({"mean": 10.2, "standard_uncertainty": 0.158113883})
        result = runner.judge(BY_ID["typea-mean-five-readings"], answer)
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual([o["ok"] for o in result["outputs"]], [True, False])

    def test_missing_output_fails(self):
        self.assertEqual(self.verdict("typea-mean-five-readings", Answer({"mean": 10.2})), "fail")

    def test_refusing_a_valid_task_fails(self):
        self.assertEqual(self.verdict("conv-inch-mm", Refusal("no")), "fail")

    def test_expected_refusal_passes(self):
        self.assertEqual(self.verdict("dim-add-length-time", Refusal("no")), "pass")

    def test_answering_where_refusal_expected_fails(self):
        self.assertEqual(self.verdict("dim-add-length-time", Answer({"value": 8.0})), "fail")

    def test_unsupported_is_its_own_verdict(self):
        self.assertEqual(self.verdict("conv-inch-mm", Unsupported("n/a")), "unsupported")
        self.assertEqual(self.verdict("dim-add-length-time", Unsupported("n/a")), "unsupported")

    def test_garbage_from_adapter_is_an_error(self):
        self.assertEqual(self.verdict("conv-inch-mm", 25.4), "error")
        self.assertEqual(self.verdict("conv-inch-mm", Answer({"value": "25.4"})), "error")


class Run(unittest.TestCase):
    def test_perfect_tool_passes_everything(self):
        report = runner.run(PAIRS, Fake(echo))
        self.assertEqual(report["summary"],
                         {"pass": len(PAIRS), "fail": 0, "unsupported": 0, "error": 0})

    def test_tool_that_always_says_one_fails_everything(self):
        def one(pair):
            outputs = pair["reference"].get("outputs", [{"name": "value"}])
            return Answer({o["name"]: 1.0 for o in outputs})
        report = runner.run(PAIRS, Fake(one))
        # 1 inch is not 1 mm, and so on; no reference answer in the file is 1.
        self.assertEqual(report["summary"]["fail"], len(PAIRS))

    def test_crashing_tool_does_not_stop_the_run(self):
        def crash(pair):
            raise RuntimeError("boom")
        report = runner.run(PAIRS, Fake(crash))
        self.assertEqual(report["summary"]["error"], len(PAIRS))
        self.assertIn("RuntimeError: boom", report["results"][0]["note"])

    def test_report_keeps_order_versions_and_counts(self):
        report = runner.run(PAIRS, Fake(echo))
        self.assertEqual([r["id"] for r in report["results"]], [p["id"] for p in PAIRS])
        self.assertEqual(report["versions"], {"fake": "0"})
        self.assertEqual(sum(report["summary"].values()), len(PAIRS))

    def test_markdown_has_one_row_per_pair(self):
        text = runner.to_markdown(runner.run(PAIRS, Fake(echo)))
        for pair in PAIRS:
            self.assertIn("| %s | pass |" % pair["id"], text)
        self.assertIn("Summary: %d pass, 0 fail, 0 unsupported, 0 error" % len(PAIRS), text)


class Model(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(model.evaluate("V * I", {"V": 10.0, "I": 2.0}), 20.0)
        self.assertEqual(model.evaluate("(a + b) / c - 2 ** 3", {"a": 1, "b": 5, "c": 2}), -5.0)
        self.assertEqual(model.evaluate("-x", {"x": 3}), -3)

    def test_everything_else_is_rejected(self):
        for bad in ("__import__('os')", "x.real", "f(x)", "x[0]", "x if x else 1",
                    "'a' * 3", "y + 1", "x +", "lambda: 1"):
            with self.subTest(expression=bad):
                with self.assertRaises(model.ModelError):
                    model.evaluate(bad, {"x": 1})


try:
    import pint  # noqa: F401
    import uncertainties  # noqa: F401
    HAVE_PINT = True
except ImportError:
    HAVE_PINT = False


@unittest.skipUnless(HAVE_PINT, "pint and uncertainties are not installed")
class PintAdapter(unittest.TestCase):
    """Checks that the adapter is wired correctly, not that Pint is right."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters.pint_uncertainties import PintUncertaintiesAdapter
        cls.adapter = PintUncertaintiesAdapter()

    def test_knows_every_unit_in_the_pairs_file(self):
        from bench.adapters.pint_uncertainties import UNITS
        used = set()
        for pair in PAIRS:
            inputs = pair["inputs"]
            used.update(v for k, v in inputs.items() if k in ("unit", "to_unit"))
            used.update(t["unit"] for t in inputs.get("terms", []))
            used.update(v["unit"] for v in inputs.get("variables", {}).values())
            used.update(c["unit"] for c in inputs.get("covariances", []))
            used.update(o["unit"] for o in pair["reference"].get("outputs", []))
        self.assertEqual(used - set(UNITS), set())
        for spelling in UNITS:
            self.adapter._unit(spelling)  # must not raise

    def test_answer_types(self):
        self.assertIsInstance(self.adapter.solve(BY_ID["conv-inch-mm"]), Answer)
        self.assertIsInstance(self.adapter.solve(BY_ID["dim-add-length-time"]), Refusal)
        self.assertIsInstance(self.adapter.solve(BY_ID["typea-mean-five-readings"]), Unsupported)

    def test_covariance_reaches_the_tool(self):
        """With the covariance removed the answer must change, from 0.007 to 0.005."""
        import copy
        pair = copy.deepcopy(BY_ID["comb-sum-with-covariance"])
        with_cov = self.adapter.solve(pair).outputs["combined_standard_uncertainty"]
        pair["inputs"]["covariances"] = []
        without = self.adapter.solve(pair).outputs["combined_standard_uncertainty"]
        self.assertAlmostEqual(with_cov, 0.007, places=12)
        self.assertAlmostEqual(without, 0.005, places=12)

    def test_incompatible_conversion_is_a_refusal(self):
        pair = {"task": "convert", "inputs": {"value": "1", "unit": "m", "to_unit": "s"},
                "reference": {"outcome": "refuse"}}
        self.assertIsInstance(self.adapter.solve(pair), Refusal)

    def test_run_has_no_errors(self):
        report = runner.run(PAIRS, self.adapter)
        self.assertEqual(report["summary"]["error"], 0)
        self.assertEqual(report["versions"]["pint"], pint.__version__)


try:
    import ucon  # noqa: F401
    HAVE_UCON = True
except ImportError:
    HAVE_UCON = False


@unittest.skipUnless(HAVE_UCON, "ucon is not installed")
class UconAdapterTests(unittest.TestCase):
    """Checks that the adapter is wired correctly, not that ucon is right."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters.ucon_adapter import UconAdapter
        cls.adapter = UconAdapter()

    def test_knows_every_unit_in_the_pairs_file(self):
        from bench.adapters.ucon_adapter import UNITS
        from bench.adapters.pint_uncertainties import UNITS as PINT_UNITS
        self.assertEqual(set(UNITS), set(PINT_UNITS))
        for spelling in UNITS:
            self.adapter._unit(spelling)  # must not raise

    def test_answer_types(self):
        self.assertIsInstance(self.adapter.solve(BY_ID["conv-inch-mm"]), Answer)
        self.assertIsInstance(self.adapter.solve(BY_ID["comb-product-uncorrelated"]), Answer)
        self.assertIsInstance(self.adapter.solve(BY_ID["dim-add-length-time"]), Refusal)
        self.assertIsInstance(self.adapter.solve(BY_ID["typea-mean-five-readings"]), Unsupported)
        self.assertIsInstance(self.adapter.solve(BY_ID["comb-sum-with-covariance"]), Unsupported)

    def test_incompatible_conversion_is_a_refusal(self):
        pair = {"task": "convert", "inputs": {"value": "1", "unit": "m", "to_unit": "s"},
                "reference": {"outcome": "refuse"}}
        self.assertIsInstance(self.adapter.solve(pair), Refusal)

    def test_an_unrelated_type_error_is_not_called_a_refusal(self):
        self.assertFalse(self.adapter._is_refusal(TypeError("bad operand type")))
        self.assertFalse(self.adapter._is_refusal(ValueError("different dimensions")))

    def test_run_has_no_errors(self):
        report = runner.run(PAIRS, self.adapter)
        self.assertEqual(report["summary"]["error"], 0)
        self.assertIn("ucon", report["versions"])


if __name__ == "__main__":
    unittest.main()
