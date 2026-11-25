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
    # ucon reads "nmi" as nano-mile (prefix n + mi), so the nautical mile is
    # given by ucon's own name for it. See results/2026-11-24-notes.md.
    "ft": "ft", "mi": "mi", "mi/h": "mi/h", "nmi": "nautical_mile",
    "km": "km", "L": "L", "m^3": "m^3", "m^2": "m^2", "in^2": "in^2",
    "atm": "atm", "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    "cal_th": "cal_th",
    # The bare word, for the question that does not say which calorie is meant.
    "cal": "cal",
    "min": "min", "h": "h",
    "mV": "mV", "ohm": "ohm",
    "1": "1",
}

# Spellings in the pairs file for which we found no unit in ucon 2.4.2.
# A pair that uses one of them is reported as unsupported, with this reason.
NO_UNIT = {
    "delta_degF": "no unit for a temperature difference in degrees Fahrenheit",
    "delta_degC": "no unit for a temperature difference in degrees Celsius",
}


def units_used(pair):
    """Every unit spelling that appears in a pair's inputs."""
    inputs = pair["inputs"]
    used = [inputs[key] for key in ("unit", "to_unit") if key in inputs]
    used += [t["unit"] for t in inputs.get("terms", [])]
    used += [v["unit"] for v in inputs.get("variables", {}).values()]
    used += [c["unit"] for c in inputs.get("covariances", [])]
    return used


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
        if task in ("convert", "add", "propagate"):
            for spelling in units_used(pair):
                if spelling in NO_UNIT:
                    return Unsupported(NO_UNIT[spelling])
        try:
            if task == "convert":
                number = self._number(inputs["value"], inputs["unit"])
                converted = number.to(self._unit(inputs["to_unit"]))
                # What ucon itself says: the unit of the result, and the name
                # it gave the unit it was asked to convert from.
                return Answer({"value": float(converted.quantity)},
                              stated={"unit": getattr(converted.unit, "shorthand", None),
                                      "reading": getattr(number.unit, "name", None)})
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
        if task == "effective_dof":
            return Unsupported("no function for effective degrees of freedom")
        if task == "round":
            return Unsupported("no function that rounds to a number of significant digits")
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
