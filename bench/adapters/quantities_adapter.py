"""Adapter for the `quantities` package (python-quantities), used as a library.

`quantities` attaches units to NumPy arrays and converts between them. It also
has `UncertainQuantity`, a quantity with an uncertainty that is carried
through arithmetic.

- `convert`, `add`: quantities with units; `rescale` converts.
- `propagate`: each variable is an `UncertainQuantity`. The package has no way
  to state a covariance between two inputs, so pairs with covariances are
  reported as unsupported.
- `type_a`, `type_b`, `effective_dof`, `round`: unsupported; the package has
  no function for them.

The adapter does no arithmetic of its own. Numbers from the pair are handed
over as Python floats.

Written by Claude (AI).
"""
from bench.model import evaluate
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> expression in the package's own unit names.
UNITS = {
    "in": "inch", "mm": "mm", "m": "m", "s": "s", "lb": "lb", "kg": "kg",
    "km/h": "km/h", "m/s": "m/s", "kW.h": "kW*h", "J": "J",
    "degC": "degC", "degF": "degF", "K": "K",
    "V": "V", "A": "A", "W": "W", "mm^2": "mm**2",
    "ft": "ft", "mi": "mile", "mi/h": "mile/h", "nmi": "nmi", "km": "km",
    "L": "L", "m^3": "m**3", "m^2": "m**2", "in^2": "inch**2",
    "atm": "atm", "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    "cal_th": "thermochemical_calorie",
    "min": "min", "h": "h", "mV": "mV", "ohm": "ohm",
    "1": "dimensionless",
    # The bare word, for the question that does not say which calorie is meant.
    "cal": "cal",
}

# Spellings for which the package has no unit that means the same.
NO_UNIT = {
    "delta_degF": "no separate unit for a temperature difference",
    "delta_degC": "no separate unit for a temperature difference",
}


def units_used(pair):
    inputs = pair["inputs"]
    used = [inputs[key] for key in ("unit", "to_unit") if key in inputs]
    used += [t["unit"] for t in inputs.get("terms", [])]
    used += [v["unit"] for v in inputs.get("variables", {}).values()]
    used += [c["unit"] for c in inputs.get("covariances", [])]
    used += [o["unit"] for o in pair["reference"].get("outputs", [])]
    return used


class QuantitiesAdapter:
    name = "quantities"

    def __init__(self):
        import quantities
        self._pq = quantities

    def versions(self):
        from importlib.metadata import version
        return {"quantities": version("quantities"), "numpy": version("numpy")}

    def _unit(self, spelling):
        # The package's own parser for unit expressions.
        return self._pq.Quantity(1.0, UNITS[spelling]).units

    def _wanted(self, pair, name):
        for output in pair["reference"].get("outputs", []):
            if output["name"] == name:
                return self._unit(output["unit"])
        return None

    def solve(self, pair):
        task, inputs = pair["task"], pair["inputs"]
        if task in ("type_a", "type_b", "effective_dof", "round"):
            return Unsupported("no function for the task %r" % task)
        if task not in ("convert", "add", "propagate"):
            return Unsupported("unknown task %r" % task)
        for spelling in units_used(pair):
            if spelling in NO_UNIT:
                return Unsupported(NO_UNIT[spelling])
        try:
            if task == "convert":
                asked = self._pq.Quantity(float(inputs["value"]), self._unit(inputs["unit"]))
                result = asked.rescale(self._unit(inputs["to_unit"]))
                return Answer({"value": float(result.magnitude)},
                              stated={"unit": result.dimensionality.string,
                                      "reading": asked.dimensionality.string})
            if task == "add":
                terms = [self._pq.Quantity(float(t["value"]), self._unit(t["unit"]))
                         for t in inputs["terms"]]
                total = terms[0]
                for term in terms[1:]:
                    total = total + term
                wanted = self._wanted(pair, "value")
                if wanted is not None:
                    total = total.rescale(wanted)
                return Answer({"value": float(total.magnitude)})
            return self._propagate(pair)
        except ValueError as exc:
            if "Unable to convert between units" in str(exc):
                return Refusal(exc)
            raise

    def _propagate(self, pair):
        inputs = pair["inputs"]
        if inputs["covariances"]:
            return Unsupported("no way to state a covariance between inputs")
        variables = {
            name: self._pq.UncertainQuantity(float(v["value"]), self._unit(v["unit"]),
                                             float(v["standard_uncertainty"]))
            for name, v in inputs["variables"].items()}
        result = evaluate(inputs["model"], variables).rescale(self._wanted(pair, "value"))
        return Answer({"value": float(result.magnitude),
                       "combined_standard_uncertainty": float(result.uncertainty.magnitude)})

    def close(self):
        pass
