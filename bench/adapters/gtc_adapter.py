"""Adapter for GTC, the GUM Tree Calculator, used as a Python library.

GTC (Measurement Standards Laboratory of New Zealand, MIT licence) works with
"uncertain numbers": a value, a standard uncertainty and degrees of freedom.
It propagates uncertainty to first order and has functions for Type A and
Type B evaluations and for effective degrees of freedom.

GTC has no units of measurement. So:

- `convert`, `add` and `round` are reported as unsupported.
- A `propagate` pair is put to GTC only when its numbers can be handed over as
  they stand. That is the case when every unit in the pair is a coherent SI
  unit without a prefix, or when all variables and the result share one unit
  (and each covariance is in that unit squared). A pair that needs a unit
  conversion on the way is reported as unsupported; the adapter does not
  convert for the tool.

One translation of inputs is made. The pairs state correlation as a
covariance, the quantity in the cited equation; GTC's `set_correlation` takes
a correlation coefficient. The adapter divides the covariance by the two
standard uncertainties, in floating point, and hands GTC the coefficient.

Type B for a normal distribution is unsupported. Our pairs state it as an
interval with a coverage probability. GTC 1.5.1 has Type B functions for
uniform, triangular, arcsine and U-shaped distributions; its "gaussian" entry
takes the standard deviation itself and returns it. `reporting.k_factor`
gives a coverage factor, but dividing the half-width by it would be the
adapter doing the calculation, so it is not used.

Numbers from the pair are handed over as Python floats.

Written by Claude (AI).
"""
from bench.model import evaluate
from bench.runner import Answer, Unsupported

# Coherent SI units without a prefix, in the spelling of the pairs file.
COHERENT = {"m", "s", "kg", "K", "A", "V", "W", "ohm", "J", "Pa",
            "m^2", "m^3", "m/s", "1"}

NO_UNITS = "GTC has no units of measurement"


class GtcAdapter:
    name = "GTC"

    def __init__(self):
        import GTC
        self._gtc = GTC

    def versions(self):
        from importlib.metadata import version
        return {"GTC": version("GTC"), "numpy": version("numpy"), "scipy": version("scipy")}

    def solve(self, pair):
        task = pair["task"]
        if task == "type_a":
            return self._type_a(pair["inputs"])
        if task == "type_b":
            return self._type_b(pair["inputs"])
        if task == "effective_dof":
            return self._effective_dof(pair["inputs"])
        if task == "propagate":
            return self._propagate(pair)
        if task == "convert":
            return Unsupported(NO_UNITS + ", so no conversion")
        if task == "add":
            return Unsupported(NO_UNITS + ", so it cannot tell whether terms are of the same kind")
        if task == "round":
            return Unsupported("no function that rounds a plain number to a number of "
                               "significant digits found in GTC")
        return Unsupported("unknown task %r" % task)

    def _type_a(self, inputs):
        estimate = self._gtc.type_a.estimate([float(r) for r in inputs["readings"]])
        return Answer({"mean": float(self._gtc.value(estimate)),
                       "standard_uncertainty": float(self._gtc.uncertainty(estimate))})

    def _type_b(self, inputs):
        functions = {"rectangular": self._gtc.type_b.uniform,
                     "triangular": self._gtc.type_b.triangular}
        if inputs["distribution"] not in functions:
            return Unsupported("no Type B function for a %s distribution stated as an "
                               "interval with a coverage probability found in GTC"
                               % inputs["distribution"])
        u = functions[inputs["distribution"]](float(inputs["half_width"]))
        return Answer({"standard_uncertainty": float(u)})

    def _effective_dof(self, inputs):
        # Each component becomes an uncertain number with value 0, the stated
        # contribution as its standard uncertainty and its degrees of freedom.
        # GTC adds them and reports the degrees of freedom of the sum.
        total = None
        for c in inputs["components"]:
            term = self._gtc.ureal(0.0, float(c["contribution"]), float(c["degrees_of_freedom"]))
            total = term if total is None else total + term
        return Answer({"effective_degrees_of_freedom": float(self._gtc.dof(total))})

    @staticmethod
    def needs_no_conversion(pair):
        """True when the pair's numbers can go to a tool without units as they stand."""
        inputs = pair["inputs"]
        units = [v["unit"] for v in inputs["variables"].values()]
        outputs = [o["unit"] for o in pair["reference"].get("outputs", [])]
        covariances = [c["unit"] for c in inputs["covariances"]]
        if not outputs:
            return False
        if all(u in COHERENT for u in units + outputs + covariances):
            return True
        one = units[0]
        return (all(u == one for u in units + outputs)
                and all(c == one + "^2" for c in covariances))

    def _propagate(self, pair):
        if not self.needs_no_conversion(pair):
            return Unsupported(NO_UNITS + "; this pair needs a unit conversion "
                               "or a check of units on the way")
        inputs = pair["inputs"]
        correlated = {name for entry in inputs["covariances"] for name in entry["between"]}
        variables = {}
        for name, v in inputs["variables"].items():
            variables[name] = self._gtc.ureal(float(v["value"]), float(v["standard_uncertainty"]),
                                              independent=name not in correlated)
        for entry in inputs["covariances"]:
            a, b = entry["between"]
            r = (float(entry["value"])
                 / (float(inputs["variables"][a]["standard_uncertainty"])
                    * float(inputs["variables"][b]["standard_uncertainty"])))
            self._gtc.set_correlation(r, variables[a], variables[b])
        result = evaluate(inputs["model"], variables)
        return Answer({"value": float(self._gtc.value(result)),
                       "combined_standard_uncertainty": float(self._gtc.uncertainty(result))})
