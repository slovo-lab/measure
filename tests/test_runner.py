"""Tests for the runner itself, using made-up tools instead of real ones.

Run: python3 -m unittest discover -s tests -v
Uses only the Python standard library. Written by Claude (AI).
"""
import os
import sys
import unittest
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from bench import model, runner  # noqa: E402
from bench.outcome import NotOffered, Refused  # noqa: E402

PAIRS = runner.load_pairs(os.path.join(ROOT, "pairs", "pairs.json"))


def pair(pair_id):
    return next(p for p in PAIRS if p["id"] == pair_id)


class Tool:
    """A made-up tool whose behaviour each test chooses."""
    name = "made-up"

    def __init__(self, behaviour):
        self._behaviour = behaviour

    def versions(self):
        return {"made-up": "0"}

    def solve(self, p):
        return self._behaviour(p)


def echo_reference(p):
    """Answers every pair with its own reference value."""
    if p["reference"].get("outcome") == "refuse":
        raise Refused("not the same kind")
    return {o["name"]: (float(Fraction(o["value"])), o["unit"]) for o in p["reference"]["outputs"]}


class RunPair(unittest.TestCase):
    def test_reference_answers_pass_every_pair(self):
        tool = Tool(echo_reference)
        for p in PAIRS:
            with self.subTest(pair=p["id"]):
                self.assertEqual(runner.run_pair(tool, p)["status"], "pass")

    def test_answer_outside_tolerance_fails(self):
        def off(p):
            answers = echo_reference(p)
            return {k: (v * (1 + 1e-6), u) for k, (v, u) in answers.items()}
        result = runner.run_pair(Tool(off), pair("conv-inch-mm"))
        self.assertEqual(result["status"], "fail")
        self.assertAlmostEqual(result["outputs"]["value"]["difference"], 1e-6, delta=1e-9)

    def test_answer_inside_tolerance_passes(self):
        def near(p):
            answers = echo_reference(p)
            return {k: (v * (1 + 1e-14), u) for k, (v, u) in answers.items()}
        self.assertEqual(runner.run_pair(Tool(near), pair("conv-mile-km"))["status"], "pass")

    def test_one_wrong_output_fails_the_pair(self):
        def wrong_uncertainty(p):
            answers = echo_reference(p)
            answers["combined_standard_uncertainty"] = (0.005, "mm")
            return answers
        result = runner.run_pair(Tool(wrong_uncertainty), pair("comb-sum-with-covariance"))
        self.assertEqual(result["status"], "fail")
        self.assertTrue(result["outputs"]["value"]["within_tolerance"])
        self.assertFalse(result["outputs"]["combined_standard_uncertainty"]["within_tolerance"])

    def test_number_for_a_must_refuse_pair_fails(self):
        result = runner.run_pair(Tool(lambda p: {"value": (8.0, "m")}), pair("dim-add-length-time"))
        self.assertEqual(result["status"], "fail")

    def test_refusing_a_must_refuse_pair_passes(self):
        def refuse(p):
            raise Refused("no")
        self.assertEqual(runner.run_pair(Tool(refuse), pair("dim-add-length-time"))["status"], "pass")

    def test_refusing_a_valid_pair_is_reported(self):
        def refuse(p):
            raise Refused("no")
        self.assertEqual(runner.run_pair(Tool(refuse), pair("dim-add-foot-inch"))["status"], "refused")

    def test_crash_is_an_error_not_a_refusal(self):
        def crash(p):
            raise RuntimeError("boom")
        result = runner.run_pair(Tool(crash), pair("dim-add-length-time"))
        self.assertEqual(result["status"], "error")
        self.assertIn("boom", result["note"])

    def test_not_offered(self):
        def none(p):
            raise NotOffered("no such feature")
        self.assertEqual(runner.run_pair(Tool(none), pair("typea-mean-five-readings"))["status"],
                         "not_offered")

    def test_missing_output_fails(self):
        def half(p):
            answers = echo_reference(p)
            answers.pop("combined_standard_uncertainty")
            return answers
        self.assertEqual(runner.run_pair(Tool(half), pair("comb-product-uncorrelated"))["status"], "fail")

    def test_answer_in_another_unit_fails(self):
        result = runner.run_pair(Tool(lambda p: {"value": (2.54, "cm")}), pair("conv-inch-mm"))
        self.assertEqual(result["status"], "fail")

    def test_not_a_number_fails(self):
        result = runner.run_pair(Tool(lambda p: {"value": (float("nan"), "mm")}), pair("conv-inch-mm"))
        self.assertEqual(result["status"], "fail")


class Summary(unittest.TestCase):
    def test_counts_add_up(self):
        run = runner.run_all([Tool(echo_reference)], PAIRS)
        table = runner.summarize(run)["made-up"]
        self.assertEqual(sum(row["pass"] for row in table.values()), len(PAIRS))
        self.assertEqual(sum(sum(row.values()) for row in table.values()), len(PAIRS))


class Model(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(model.evaluate("2 * a + 3 * b", {"a": 1, "b": 2}), 8)
        self.assertEqual(model.evaluate("-a / b ** 2", {"a": 8, "b": 2}), -2)

    def test_variables_in_order(self):
        self.assertEqual(model.variables_in("V * I + V"), ["V", "I"])

    def test_rejects_calls_and_attributes(self):
        for text in ("__import__('os')", "a.b", "a[0]", "lambda: 1", "a if b else c", "'x'"):
            with self.subTest(text=text):
                with self.assertRaises(model.ModelError):
                    model.evaluate(text, {"a": 1, "b": 2, "c": 3})

    def test_unknown_variable(self):
        with self.assertRaises(model.ModelError):
            model.evaluate("a + z", {"a": 1})

    def test_every_model_in_the_file_uses_only_its_variables(self):
        for p in PAIRS:
            if p["task"] == "propagate":
                with self.subTest(pair=p["id"]):
                    self.assertEqual(set(model.variables_in(p["inputs"]["model"])),
                                     set(p["inputs"]["variables"]))


if __name__ == "__main__":
    unittest.main()
