"""Tests for the runner itself, using made-up adapters with known behaviour.

Run: python3 -m unittest discover -s tests -v
Written by Claude (AI).
"""
import copy
import json
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

    def test_temperature_difference_is_not_treated_as_a_temperature(self):
        answer = self.adapter.solve(BY_ID["conv-degf-interval-k"])
        self.assertAlmostEqual(answer.outputs["value"], 5.0, places=9)

    def test_new_tasks_are_unsupported(self):
        for pair_id in ("dof-welch-satterthwaite-two", "round-half-even-stays",
                        "typeb-normal-95-interval"):
            self.assertIsInstance(self.adapter.solve(BY_ID[pair_id]), Unsupported)

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
        from bench.adapters.ucon_adapter import NO_UNIT
        self.assertEqual(set(UNITS) | set(NO_UNIT), set(PINT_UNITS))
        self.assertEqual(set(UNITS) & set(NO_UNIT), set())
        for spelling in UNITS:
            self.adapter._unit(spelling)  # must not raise

    def test_a_pair_with_a_unit_ucon_lacks_is_unsupported(self):
        answer = self.adapter.solve(BY_ID["conv-degf-interval-k"])
        self.assertIsInstance(answer, Unsupported)
        self.assertIn("temperature difference", answer.reason)

    def test_new_tasks_are_unsupported(self):
        for pair_id in ("dof-welch-satterthwaite-two", "round-half-even-stays",
                        "typeb-normal-95-interval"):
            self.assertIsInstance(self.adapter.solve(BY_ID[pair_id]), Unsupported)

    def test_mass_to_length_is_a_refusal(self):
        self.assertIsInstance(self.adapter.solve(BY_ID["dim-convert-mass-length"]), Refusal)

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


try:
    import GTC  # noqa: F401
    HAVE_GTC = True
except ImportError:
    HAVE_GTC = False


@unittest.skipUnless(HAVE_GTC, "GTC is not installed")
class GtcAdapterTests(unittest.TestCase):
    """Checks that the adapter is wired correctly, not that GTC is right."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters.gtc_adapter import GtcAdapter
        cls.adapter = GtcAdapter()

    def test_tasks_that_need_units_are_unsupported(self):
        for pair_id in ("conv-inch-mm", "dim-add-length-time", "dim-add-foot-inch",
                        "dim-convert-mass-length", "round-half-even-stays"):
            self.assertIsInstance(self.adapter.solve(BY_ID[pair_id]), Unsupported)

    def test_a_pair_that_needs_a_conversion_is_not_sent(self):
        self.assertFalse(self.adapter.needs_no_conversion(BY_ID["comb-product-mixed-units"]))
        self.assertIsInstance(self.adapter.solve(BY_ID["comb-product-mixed-units"]), Unsupported)

    def test_which_propagation_pairs_are_sent(self):
        sent = {p["id"] for p in PAIRS
                if p["task"] == "propagate" and self.adapter.needs_no_conversion(p)}
        self.assertEqual(sent, {
            "comb-product-uncorrelated", "comb-quotient-uncorrelated",
            "comb-sum-with-covariance", "comb-difference-with-covariance",
            "comb-square-same-variable", "comb-square-as-power", "comb-linear-combination"})

    def test_one_shared_unit_is_not_enough_when_the_result_differs(self):
        pair = {"task": "propagate",
                "inputs": {"model": "a * b", "covariances": [], "variables": {
                    "a": {"value": "1", "standard_uncertainty": "0.1", "unit": "mm"},
                    "b": {"value": "1", "standard_uncertainty": "0.1", "unit": "mm"}}},
                "reference": {"outputs": [{"name": "value", "unit": "mm^2"}]}}
        self.assertFalse(self.adapter.needs_no_conversion(pair))

    def test_normal_type_b_is_unsupported(self):
        self.assertIsInstance(self.adapter.solve(BY_ID["typeb-normal-95-interval"]), Unsupported)

    def test_answer_types(self):
        for pair_id in ("typea-mean-five-readings", "typeb-rectangular-half-width",
                        "typeb-triangular-half-width", "dof-welch-satterthwaite-two",
                        "comb-sum-with-covariance"):
            self.assertIsInstance(self.adapter.solve(BY_ID[pair_id]), Answer)

    def test_covariance_reaches_the_tool(self):
        # With the covariance left out the sum would have uncertainty 0.005, not 0.007.
        answer = self.adapter.solve(BY_ID["comb-sum-with-covariance"])
        self.assertAlmostEqual(answer.outputs["combined_standard_uncertainty"], 0.007, places=12)

    def test_degrees_of_freedom_come_from_the_tool(self):
        answer = self.adapter.solve(BY_ID["dof-welch-satterthwaite-two"])
        self.assertTrue(12 < answer.outputs["effective_degrees_of_freedom"] < 13)

    def test_run_has_no_errors(self):
        report = runner.run(PAIRS, self.adapter)
        self.assertEqual(report["summary"]["error"], 0)
        self.assertIn("GTC", report["versions"])


def _have(module, command):
    try:
        __import__(module)
        __import__("mcp")
        from bench.mcp_client import find_command
        find_command(command)
        return True
    except Exception:
        return False


HAVE_UCON_MCP = _have("ucon", "ucon-mcp")
HAVE_UNIT_CONVERTER_MCP = _have("unit_converter_mcp", "unit-converter-mcp")


class ServerAdapterBase:
    """Shared checks for adapters that talk to a server for AI agents."""
    adapter_class = None

    @classmethod
    def setUpClass(cls):
        from bench.mcp_client import ServerError
        try:
            cls.adapter = cls.adapter_class()
        except ServerError as exc:
            # Installed, but it does not start with this Python: nothing to test here.
            raise unittest.SkipTest(str(exc))
        cls.report = runner.run(PAIRS, cls.adapter)

    @classmethod
    def tearDownClass(cls):
        cls.adapter.close()

    def result(self, pair_id):
        return next(r for r in self.report["results"] if r["id"] == pair_id)

    def test_run_has_no_errors(self):
        errors = [(r["id"], r["note"]) for r in self.report["results"] if r["verdict"] == "error"]
        self.assertEqual(errors, [])

    def test_only_conversions_are_attempted(self):
        task = {p["id"]: p["task"] for p in PAIRS}
        for r in self.report["results"]:
            if task[r["id"]] != "convert":
                with self.subTest(pair=r["id"]):
                    self.assertEqual(r["verdict"], "unsupported")

    def test_the_answer_comes_from_the_server(self):
        self.assertTrue(self.adapter._server.server_name)
        self.assertEqual(self.result("conv-inch-mm")["outputs"][0]["got"], 25.4)

    def test_mass_to_length_is_a_refusal(self):
        r = self.result("dim-convert-mass-length")
        self.assertEqual(r["verdict"], "pass")
        self.assertTrue(r["note"].startswith("refused"))

    # True for servers that have units for temperature differences.
    expects_differences = False

    def test_temperature_difference_is_not_sent_as_a_temperature(self):
        expected = "pass" if self.expects_differences else "unsupported"
        self.assertEqual(self.result("conv-degc-interval-k")["verdict"], expected)

    def test_notes_fit_on_one_line(self):
        for r in self.report["results"]:
            self.assertNotIn("\n", r["note"])


@unittest.skipUnless(HAVE_UCON_MCP, "ucon-tools[mcp] is not installed")
class UconMcpAdapterTests(ServerAdapterBase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from bench.adapters.ucon_mcp import UconMcpAdapter
        cls.adapter_class = UconMcpAdapter
        super().setUpClass()


@unittest.skipUnless(HAVE_UNIT_CONVERTER_MCP, "unit-converter-mcp is not installed")
class UnitConverterMcpAdapterTests(ServerAdapterBase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from bench.adapters.unit_converter_mcp import UnitConverterMcpAdapter
        cls.adapter_class = UnitConverterMcpAdapter
        super().setUpClass()

    def test_knows_every_unit_used_in_conversions(self):
        from bench.adapters.unit_converter_mcp import NO_UNIT, UNITS
        for p in PAIRS:
            if p["task"] == "convert":
                for unit in (p["inputs"]["unit"], p["inputs"]["to_unit"]):
                    with self.subTest(pair=p["id"], unit=unit):
                        self.assertTrue(unit in UNITS or unit in NO_UNIT)


HAVE_MCP_UNITS = _have("mcp_units", "mcp-units")
HAVE_MCP_GNU_UNITS = _have("mcp", "mcp-gnu-units")


@unittest.skipUnless(HAVE_MCP_UNITS, "mcp-units is not installed")
class McpUnitsAdapterTests(ServerAdapterBase, unittest.TestCase):
    expects_differences = True

    @classmethod
    def setUpClass(cls):
        from bench.adapters.mcp_units import McpUnitsAdapter
        cls.adapter_class = McpUnitsAdapter
        super().setUpClass()


@unittest.skipUnless(HAVE_MCP_GNU_UNITS, "mcp-gnu-units is not installed or not pointed to")
class McpGnuUnitsAdapterTests(ServerAdapterBase, unittest.TestCase):
    expects_differences = True

    @classmethod
    def setUpClass(cls):
        from bench.adapters.mcp_gnu_units import McpGnuUnitsAdapter
        cls.adapter_class = McpGnuUnitsAdapter
        super().setUpClass()

    def test_a_temperature_is_written_as_a_function(self):
        # 25 degC as a temperature is 298.15 K; as a difference it would be 25 K.
        self.assertEqual(self.result("conv-degc-k")["verdict"], "pass")


HAVE_MU_MCP = _have("measurement_uncertainty_mcp", "measurement-uncertainty-mcp")


@unittest.skipUnless(HAVE_MU_MCP, "measurement-uncertainty-mcp is not installed")
class MeasurementUncertaintyMcpAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from bench.adapters.measurement_uncertainty_mcp import MeasurementUncertaintyMcpAdapter
        cls.adapter = MeasurementUncertaintyMcpAdapter()
        cls.report = runner.run(PAIRS, cls.adapter)

    @classmethod
    def tearDownClass(cls):
        cls.adapter.close()

    def result(self, pair_id):
        return next(r for r in self.report["results"] if r["id"] == pair_id)

    def test_run_has_no_errors(self):
        errors = [(r["id"], r["note"]) for r in self.report["results"] if r["verdict"] == "error"]
        self.assertEqual(errors, [])

    def test_only_its_three_tasks_are_attempted(self):
        task = {p["id"]: p["task"] for p in PAIRS}
        for r in self.report["results"]:
            if task[r["id"]] not in ("type_a", "type_b", "effective_dof"):
                with self.subTest(pair=r["id"]):
                    self.assertEqual(r["verdict"], "unsupported")

    def test_type_a_returns_both_outputs_from_the_server(self):
        outputs = {o["name"]: o["got"] for o in self.result("typea-mean-five-readings")["outputs"]}
        self.assertEqual(set(outputs), {"mean", "standard_uncertainty"})
        self.assertIsInstance(outputs["standard_uncertainty"], float)

    def test_coverage_probability_is_not_turned_into_a_factor_by_the_adapter(self):
        self.assertEqual(self.result("typeb-normal-95-interval")["verdict"], "unsupported")

    def test_propagation_is_not_done_by_the_adapter(self):
        self.assertEqual(self.result("comb-product-uncorrelated")["verdict"], "unsupported")


class McpClient(unittest.TestCase):
    def test_missing_command_is_reported(self):
        from bench.mcp_client import ServerError, find_command
        with self.assertRaises(ServerError):
            find_command("no-such-server-command-for-measure")



class VersionTwo(unittest.TestCase):
    """The proposed format version 2: several right answers, labels, relations."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "pairs", "proposed-v2.json"), encoding="utf-8") as handle:
            cls.items = {item["id"]: item for item in json.load(handle)["pairs"]}

    class Fixed:
        """An adapter that gives prepared answers, by task and inputs."""
        name = "fixed"

        def __init__(self, answer):
            self.answer = answer
            self.seen = []

        def versions(self):
            return {}

        def solve(self, pair):
            self.seen.append(pair)
            return self.answer(pair) if callable(self.answer) else self.answer

    def verdict(self, pid, answer):
        report = runner.run([self.items[pid]], self.Fixed(answer))
        return report["results"][0]["verdict"], report

    def test_one_answer_with_its_reading_passes(self):
        verdict, _ = self.verdict("amb-calorie-joule",
                                  runner.Answer({"value": 4.184}, stated={"reading": "Thermochemical calorie"}))
        self.assertEqual(verdict, "pass")

    def test_one_answer_without_a_word_is_incomplete(self):
        verdict, report = self.verdict("amb-calorie-joule", runner.Answer({"value": 4.1868}, stated={}))
        self.assertEqual(verdict, "incomplete")
        self.assertEqual(report["summary"]["incomplete"], 1)

    def test_one_answer_with_an_unhelpful_word_is_incomplete(self):
        verdict, _ = self.verdict("amb-calorie-joule",
                                  runner.Answer({"value": 4.184}, stated={"reading": "calorie"}))
        self.assertEqual(verdict, "incomplete")

    def test_one_answer_naming_the_other_reading_fails(self):
        verdict, _ = self.verdict("amb-calorie-joule",
                                  runner.Answer({"value": 4.184}, stated={"reading": "International Table"}))
        self.assertEqual(verdict, "fail")

    def test_all_answers_pass(self):
        verdict, _ = self.verdict("amb-calorie-joule",
                                  runner.Answer({"value": 4.184}, also=[{"value": 4.1868}]))
        self.assertEqual(verdict, "pass")

    def test_a_number_that_is_no_answer_fails(self):
        verdict, _ = self.verdict("amb-calorie-joule", runner.Answer({"value": 4.19}, stated={}))
        self.assertEqual(verdict, "fail")

    def test_declining_passes_when_the_pair_says_so(self):
        verdict, _ = self.verdict("amb-calorie-joule", runner.Refusal("which calorie?"))
        self.assertEqual(verdict, "pass")
        item = copy.deepcopy(self.items["amb-calorie-joule"])
        item["reference"]["refusal_passes"] = False
        report = runner.run([item], self.Fixed(runner.Refusal("which calorie?")))
        self.assertEqual(report["results"][0]["verdict"], "fail")

    def test_adapter_that_reports_no_statements_is_not_blamed_on_the_tool(self):
        verdict, report = self.verdict("amb-calorie-joule", runner.Answer({"value": 4.184}))
        self.assertEqual(verdict, "unsupported")
        self.assertIn("adapter", report["results"][0]["note"])

    def test_adapter_never_sees_the_answers(self):
        adapter = self.Fixed(runner.Answer({"value": 4.184}, stated={}))
        runner.run([self.items["amb-calorie-joule"]], adapter)
        self.assertNotIn("4.184", json.dumps(adapter.seen))
        self.assertEqual(adapter.seen[0]["reference"], {"outputs": [{"name": "value", "unit": "J"}]})

    def test_label_present_and_right(self):
        verdict, _ = self.verdict("lab-inch-mm-states-unit",
                                  runner.Answer({"value": 25.4}, stated={"unit": "MM"}))
        self.assertEqual(verdict, "pass")

    def test_label_missing_is_incomplete(self):
        verdict, _ = self.verdict("lab-inch-mm-states-unit", runner.Answer({"value": 25.4}, stated={}))
        self.assertEqual(verdict, "incomplete")

    def test_label_wrong_fails(self):
        verdict, _ = self.verdict("lab-inch-mm-states-unit",
                                  runner.Answer({"value": 25.4}, stated={"unit": "cm"}))
        self.assertEqual(verdict, "fail")

    def test_wrong_number_fails_whatever_the_label(self):
        verdict, _ = self.verdict("lab-inch-mm-states-unit",
                                  runner.Answer({"value": 2.54}, stated={"unit": "mm"}))
        self.assertEqual(verdict, "fail")

    def test_round_trip_feeds_the_tools_own_answer_back(self):
        def answer(pair):
            value = float(pair["inputs"]["value"])
            return runner.Answer({"value": value * 25.4 if pair["inputs"]["unit"] == "in" else value / 25.4})
        adapter = self.Fixed(answer)
        report = runner.run([self.items["rel-inch-mm-round-trip"]], adapter)
        self.assertEqual(report["results"][0]["verdict"], "pass")
        self.assertEqual(float(adapter.seen[1]["inputs"]["value"]), 7 * 25.4)

    def test_round_trip_with_two_different_factors_fails(self):
        def answer(pair):
            value = float(pair["inputs"]["value"])
            return runner.Answer({"value": value * 25.4 if pair["inputs"]["unit"] == "in" else value / 25.0})
        verdict, _ = self.verdict("rel-inch-mm-round-trip", answer)
        self.assertEqual(verdict, "fail")

    def test_relation_between_two_calls(self):
        def same(pair):
            return runner.Answer({"value": 4.0, "combined_standard_uncertainty": 0.04})
        def differs(pair):
            u = 0.04 if "**" in pair["inputs"]["model"] else 0.0282842712474619
            return runner.Answer({"value": 4.0, "combined_standard_uncertainty": u})
        self.assertEqual(self.verdict("rel-square-two-ways", same)[0], "pass")
        self.assertEqual(self.verdict("rel-square-two-ways", differs)[0], "fail")

    def test_relation_unsupported_and_refused(self):
        self.assertEqual(self.verdict("rel-square-two-ways", runner.Unsupported("no"))[0], "unsupported")
        self.assertEqual(self.verdict("rel-square-two-ways", runner.Refusal("no"))[0], "fail")

    def test_relation_with_a_crashing_tool_is_an_error(self):
        def crash(pair):
            raise RuntimeError("boom")
        self.assertEqual(self.verdict("rel-inch-mm-round-trip", crash)[0], "error")

    def test_version_one_report_has_the_same_four_counts(self):
        report = runner.run(PAIRS, Fake(echo))
        self.assertEqual(sorted(report["summary"]), sorted(runner.VERDICTS))


if __name__ == "__main__":
    unittest.main()
