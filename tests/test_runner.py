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


def units_in(pair):
    """Every unit spelling a pair uses, in its inputs and its reference."""
    inputs = pair["inputs"]
    used = [inputs[key] for key in ("unit", "to_unit") if key in inputs]
    used += [t["unit"] for t in inputs.get("terms", [])]
    used += [v["unit"] for v in inputs.get("variables", {}).values()]
    used += [c["unit"] for c in inputs.get("covariances", [])]
    used += [o["unit"] for o in pair["reference"].get("outputs", [])]
    return used


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



try:
    import metrolopy  # noqa: F401
    HAVE_METROLOPY = True
except ImportError:
    HAVE_METROLOPY = False


@unittest.skipUnless(HAVE_METROLOPY, "metrolopy is not installed")
class MetrolopyAdapterTests(unittest.TestCase):
    """Checks that the adapter is wired correctly, not that MetroloPy is right."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters.metrolopy_adapter import MetrolopyAdapter, UNITS
        cls.adapter = MetrolopyAdapter()
        cls.units = UNITS

    def test_knows_every_unit_in_the_pairs_file(self):
        used = set()
        for pair in PAIRS:
            used.update(units_in(pair))
        self.assertEqual(used - set(self.units), set())

    def test_every_pair_gets_an_answer_without_an_error(self):
        report = runner.run(PAIRS, self.adapter)
        self.assertEqual(report["summary"]["error"], 0)

    def test_only_rounding_is_unsupported(self):
        report = runner.run(PAIRS, self.adapter)
        unsupported = {r["id"] for r in report["results"] if r["verdict"] == "unsupported"}
        self.assertEqual(unsupported, {p["id"] for p in PAIRS if p["task"] == "round"})

    def test_refuses_to_add_a_length_and_a_time(self):
        self.assertIsInstance(self.adapter.solve(BY_ID["dim-add-length-time"]), Refusal)

    def test_reports_what_the_library_states(self):
        answer = self.adapter.solve(BY_ID["conv-inch-mm"])
        self.assertEqual(answer.stated["unit"], "mm")


try:
    import quantities  # noqa: F401
    HAVE_QUANTITIES = True
except ImportError:
    HAVE_QUANTITIES = False


@unittest.skipUnless(HAVE_QUANTITIES, "quantities is not installed")
class QuantitiesAdapterTests(unittest.TestCase):
    """Checks that the adapter is wired correctly, not that quantities is right."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters.quantities_adapter import NO_UNIT, QuantitiesAdapter, UNITS
        cls.adapter = QuantitiesAdapter()
        cls.known = set(UNITS) | set(NO_UNIT)

    def test_knows_every_unit_in_the_pairs_file(self):
        used = set()
        for pair in PAIRS:
            used.update(units_in(pair))
        self.assertEqual(used - self.known, set())

    def test_every_pair_gets_an_answer_without_an_error(self):
        report = runner.run(PAIRS, self.adapter)
        self.assertEqual(report["summary"]["error"], 0)

    def test_covariance_is_unsupported_not_ignored(self):
        self.assertIsInstance(self.adapter.solve(BY_ID["comb-sum-with-covariance"]), Unsupported)

    def test_refuses_to_add_a_length_and_a_time(self):
        self.assertIsInstance(self.adapter.solve(BY_ID["dim-add-length-time"]), Refusal)

    def test_numbers_come_from_the_library(self):
        """The adapter hands the library's own number back, right or wrong."""
        import quantities as pq
        own = float(pq.Quantity(150.0, "lb").rescale("kg").magnitude)
        self.assertEqual(self.adapter.solve(BY_ID["conv-pound-kg"]).outputs["value"], own)

    def test_a_temperature_is_not_offered_but_a_difference_is(self):
        """The package documents its degC as a difference with no offset."""
        self.assertIsInstance(self.adapter.solve(BY_ID["conv-degc-k"]), Unsupported)
        self.assertEqual(self.adapter.solve(BY_ID["conv-degc-interval-k"]).outputs["value"], 15.0)


def _importable(*modules):
    import importlib.util
    return all(importlib.util.find_spec(m) is not None for m in modules)


@unittest.skipUnless(_importable("astropy", "unyt"), "astropy and unyt are not installed")
class AstropyAndUnytAdapterTests(unittest.TestCase):
    """Checks that the two adapters are wired correctly, not that the packages are right."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters.astropy_adapter import AstropyAdapter
        from bench.adapters.unyt_adapter import UnytAdapter
        cls.adapters = [AstropyAdapter(), UnytAdapter()]

    def test_know_every_unit_in_the_pairs_file(self):
        used = set()
        for pair in PAIRS:
            used.update(units_in(pair))
        for adapter in self.adapters:
            self.assertEqual(used - set(adapter.units) - set(adapter.no_unit), set(), adapter.name)

    def test_every_pair_gets_an_answer_without_an_error(self):
        for adapter in self.adapters:
            report = runner.run(PAIRS, adapter)
            self.assertEqual(report["summary"]["error"], 0, adapter.name)

    def test_refuse_to_add_a_length_and_a_time(self):
        for adapter in self.adapters:
            self.assertIsInstance(adapter.solve(BY_ID["dim-add-length-time"]), Refusal, adapter.name)

    def test_astropy_number_comes_from_the_library(self):
        import astropy.units as u
        own = float((150.0 * u.imperial.lb).to(u.kg).value)
        self.assertEqual(self.adapters[0].solve(BY_ID["conv-pound-kg"]).outputs["value"], own)

    def test_astropy_temperature_uses_the_documented_equivalency(self):
        import astropy.units as u
        own = float((25.0 * u.deg_C).to(u.K, equivalencies=u.temperature()).value)
        self.assertEqual(self.adapters[0].solve(BY_ID["conv-degc-k"]).outputs["value"], own)

    def test_unyt_number_comes_from_the_library(self):
        import unyt
        own = float(unyt.unyt_quantity(150.0, "lb").to("kg"))
        self.assertEqual(self.adapters[1].solve(BY_ID["conv-pound-kg"]).outputs["value"], own)


def _node_ready():
    try:
        from bench.node_client import library_version
        library_version("mathjs")
        library_version("js-quantities")
        return True
    except Exception:
        return False


@unittest.skipUnless(_node_ready(), "node, mathjs or js-quantities is not installed")
class NodeAdapterTests(unittest.TestCase):
    """Checks that the two JavaScript adapters are wired correctly."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters import js_quantities_adapter, mathjs_adapter
        cls.adapters = [mathjs_adapter.MathjsAdapter(),
                        js_quantities_adapter.JsQuantitiesAdapter()]

    def test_know_every_unit_in_the_pairs_file(self):
        used = set()
        for pair in PAIRS:
            used.update(units_in(pair))
        for adapter in self.adapters:
            self.assertEqual(used - set(adapter.units) - set(adapter.no_unit), set(), adapter.name)

    def test_every_pair_gets_an_answer_without_an_error(self):
        for adapter in self.adapters:
            report = runner.run(PAIRS, adapter)
            self.assertEqual(report["summary"]["error"], 0, adapter.name)

    def test_refuse_to_add_a_length_and_a_time(self):
        for adapter in self.adapters:
            self.assertIsInstance(adapter.solve(BY_ID["dim-add-length-time"]), Refusal, adapter.name)

    def test_the_number_and_the_unit_come_from_the_library(self):
        from bench.node_client import ask
        own = ask({"library": "js-quantities", "op": "convert", "value": 150.0,
                   "unit": "lb", "to_unit": "kg"})
        answer = self.adapters[1].solve(BY_ID["conv-pound-kg"])
        self.assertEqual(answer.outputs["value"], own["value"])
        self.assertEqual(answer.stated["unit"], own["unit"])

    def test_js_quantities_is_asked_about_a_temperature_not_a_difference(self):
        adapter = self.adapters[1]
        self.assertEqual(adapter._names(None, ["degC", "K"]), ["tempC", "tempK"])
        self.assertEqual(adapter._names(None, ["delta_degC", "K"]), ["degC", "degK"])

    def test_versions_name_the_library_and_node(self):
        for adapter in self.adapters:
            self.assertEqual(set(adapter.versions()), {adapter.library, "node"})


def _calculator_ready():
    try:
        from bench.mcp_client import find_command
        import mcp  # noqa: F401
        find_command("p6plab-mcp-calculator")
        return True
    except Exception:
        return False


@unittest.skipUnless(_calculator_ready(), "p6plab-mcp-calculator is not installed")
class P6plabCalculatorAdapterTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from bench.adapters.p6plab_calculator import P6plabCalculatorAdapter
        cls.adapter = P6plabCalculatorAdapter()

    @classmethod
    def tearDownClass(cls):
        cls.adapter.close()

    def test_every_pair_gets_an_answer_without_an_error(self):
        report = runner.run(PAIRS, self.adapter)
        self.assertEqual(report["summary"]["error"], 0)

    def test_rounding_is_answered_by_the_server(self):
        answer = self.adapter.solve(BY_ID["round-above-half-goes-up"])
        self.assertIsInstance(answer.outputs["value"], float)

    def test_a_conversion_is_not_offered_and_the_note_quotes_the_server(self):
        answer = self.adapter.solve(BY_ID["conv-inch-mm"])
        self.assertIsInstance(answer, Unsupported)
        self.assertIn("not yet implemented", answer.reason)


class DecimalPlaces(unittest.TestCase):
    """Significant digits restated as decimal places, for a tool that takes those."""

    def test_examples(self):
        from bench.adapters.p6plab_calculator import decimal_places
        self.assertEqual(decimal_places("2.675", 3), 2)
        self.assertEqual(decimal_places("1.2501", 2), 1)
        self.assertEqual(decimal_places("0.01234", 2), 3)
        self.assertEqual(decimal_places("1234", 2), -2)


@unittest.skipUnless(HAVE_UCON_MCP and HAVE_UNIT_CONVERTER_MCP and HAVE_MCP_UNITS
                     and HAVE_MCP_GNU_UNITS, "the four converting servers are not installed")
class ServersSayWhatTheyRead(unittest.TestCase):
    """The server adapters hand over what the server's reply says, not a guess."""

    @classmethod
    def setUpClass(cls):
        from bench.adapters.mcp_gnu_units import McpGnuUnitsAdapter
        from bench.adapters.mcp_units import McpUnitsAdapter
        from bench.adapters.ucon_mcp import UconMcpAdapter
        from bench.adapters.unit_converter_mcp import UnitConverterMcpAdapter
        cls.adapters = {a.name: a for a in (UconMcpAdapter(), UnitConverterMcpAdapter(),
                                            McpUnitsAdapter(), McpGnuUnitsAdapter())}
        with open(os.path.join(ROOT, "pairs", "proposed-v2.json"), encoding="utf-8") as handle:
            cls.items = {item["id"]: item for item in json.load(handle)["pairs"]}

    @classmethod
    def tearDownClass(cls):
        for adapter in cls.adapters.values():
            adapter.close()

    def test_every_server_states_the_unit_of_its_result(self):
        for name, adapter in self.adapters.items():
            answer = adapter.solve(BY_ID["conv-inch-mm"])
            self.assertTrue(answer.stated and answer.stated.get("unit"), name)

    def test_no_error_on_the_proposed_questions(self):
        for name, adapter in self.adapters.items():
            report = runner.run(list(self.items.values()), adapter)
            self.assertEqual(report["summary"]["error"], 0, name)

    def test_a_bare_ton_is_turned_down_by_the_two_servers_with_fixed_lists(self):
        for name in ("ucon-mcp (server)", "unit-converter-mcp (server)"):
            self.assertIsInstance(self.adapters[name].solve(self.items["amb-ton-kilogram"]),
                                  Refusal, name)


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
