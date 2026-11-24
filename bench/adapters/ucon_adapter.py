"""Adapter for ucon (https://pypi.org/project/ucon/), used as a Python library.

ucon converts units, checks dimensions and propagates standard uncertainties
through arithmetic on its `Number` type. In version 2.4.2 we found no way to
state a covariance between inputs and no function that returns the standard
uncertainty of a mean or of a rectangular distribution, so those tasks are
reported as unsupported; the adapter does not do the calculation itself.

ucon's server for AI agents is a separate thing and is not tested here.

Written by Claude (AI).
"""
from bench.model import evaluate
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> spelling ucon's parser understands.
UNITS = {
    "in": "in", "mm": "mm", "m": "m", "s": "s",
    "lb": "lb", "kg": "kg",
    "km/h": "km/h", "m/s": "m/s",
    "kW.h": "kW*h", "J": "J",
    "degC": "degC", "degF": "degF", "K": "K",
    "V": "V", "A": "A", "W": "W",
    "mm^2": "mm^2",
}


class UconAdapter:
    name = "ucon"

    def __init__(self):
        import ucon
        self._ucon = ucon

    def versions(self):
        from importlib.metadata import version
        return {"ucon": version("ucon")}

    def _unit(self, spelling):
        return self._ucon.parse_unit(UNITS[spelling])

    def _number(self, value, unit, uncertainty=None):
        return self._ucon.Number(float(value), self._unit(unit), uncertainty=uncertainty)

    def _is_refusal(self, exc):
        """True if the exception is ucon declining a dimensionally wrong request."""
        if isinstance(exc, self._ucon.DimensionMismatch):
            return True
        return isinstance(exc, TypeError) and "different dimensions" in str(exc)

    def solve(self, pair):
        task = pair["task"]
        inputs = pair["inputs"]
        try:
            if task == "convert":
                number = self._number(inputs["value"], inputs["unit"])
                converted = number.to(self._unit(inputs["to_unit"]))
                return Answer({"value": float(converted.quantity)})
            if task == "add":
                return self._add(pair)
            if task == "propagate":
                return self._propagate(pair)
        except Exception as exc:
            if self._is_refusal(exc):
                return Refusal(exc)
            raise
        if task == "type_a":
            return Unsupported("has mean() and std() for arrays, but no function that returns "
                               "the standard uncertainty of the mean")
        if task == "type_b":
            return Unsupported("no function for a Type B evaluation")
        return Unsupported("unknown task %r" % task)

    def _add(self, pair):
        terms = [self._number(t["value"], t["unit"]) for t in pair["inputs"]["terms"]]
        total = terms[0]
        for term in terms[1:]:
            total = total + term
        outputs = pair["reference"].get("outputs")
        if outputs:
            total = total.to(self._unit(outputs[0]["unit"]))
        return Answer({"value": float(total.quantity)})

    def _propagate(self, pair):
        inputs = pair["inputs"]
        if inputs["covariances"]:
            return Unsupported("no way to state a covariance between inputs")
        variables = {
            name: self._number(v["value"], v["unit"], float(v["standard_uncertainty"]))
            for name, v in inputs["variables"].items()
        }
        result = evaluate(inputs["model"], variables)
        units = {o["name"]: o["unit"] for o in pair["reference"]["outputs"]}
        result = result.to(self._unit(units["value"]))
        if result.uncertainty is None:
            return Answer({"value": float(result.quantity)})
        return Answer({"value": float(result.quantity),
                       "combined_standard_uncertainty": float(result.uncertainty)})
