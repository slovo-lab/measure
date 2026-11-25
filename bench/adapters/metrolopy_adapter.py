"""Adapter for MetroloPy, used as a Python library.

MetroloPy (H. V. Parks) works with "gummys": a value, a standard uncertainty,
degrees of freedom and a unit. It converts units, propagates uncertainty to
first order with correlations, has probability distributions for Type B
evaluations, and combines degrees of freedom.

What is handed to the library, and what is read back:

- `convert`, `add`: gummys with units; the library converts and adds.
- `propagate`: independent variables are gummys with a standard uncertainty.
  Correlated variables are made with `gummy.create` and a covariance matrix,
  the quantity our pairs state. A covariance given in another unit than the
  product of the two variables' units is first converted by the library.
- `type_a`: `metrolopy.mean` of the readings.
- `type_b`: a gummy made from `UniformDist` or `TriangularDist`; for a normal
  distribution, a gummy made from the half-width as an expanded uncertainty
  with the coverage probability `p`. In each case the library's own `.u` is
  read back.
- `effective_dof`: the contributions are added as gummys of value 0 with
  their degrees of freedom, and the library's `.dof` of the sum is read back.
- `round`: unsupported. The library rounds when it prints a gummy, by its
  uncertainty; it has no function that rounds a bare number to a count of
  significant digits.

The adapter does no arithmetic of its own. Numbers from the pair are handed
over as Python floats.

Written by Claude (AI).
"""
from bench.model import evaluate
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> spelling MetroloPy understands.
UNITS = {
    "in": "in", "mm": "mm", "m": "m", "s": "s", "lb": "lb", "kg": "kg",
    "km/h": "km/h", "m/s": "m/s", "kW.h": "kW h", "J": "J",
    "degC": "degC", "degF": "degF", "K": "K",
    "V": "V", "A": "A", "W": "W", "mm^2": "mm**2",
    "ft": "ft", "mi": "mi", "mi/h": "mi/h", "nmi": "nmi", "km": "km",
    "L": "L", "m^3": "m**3", "m^2": "m**2", "in^2": "in**2",
    "atm": "atm", "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    "cal_th": "thermochemical calorie",
    "min": "min", "h": "h", "mV": "mV", "ohm": "ohm",
    # MetroloPy has separate units for temperature intervals.
    "delta_degF": "degF-i", "delta_degC": "degC-i",
    "1": "1",
    # The bare word, for the question that does not say which calorie is meant.
    "cal": "cal",
}


class MetrolopyAdapter:
    name = "MetroloPy"

    def __init__(self):
        import metrolopy
        self._m = metrolopy

    def versions(self):
        from importlib.metadata import version
        return {"metrolopy": version("metrolopy"), "numpy": version("numpy"),
                "scipy": version("scipy")}

    def _gummy(self, value, unit, u=0):
        return self._m.gummy(float(value), float(u), unit=UNITS[unit])

    def _wanted(self, pair, name):
        for output in pair["reference"].get("outputs", []):
            if output["name"] == name:
                return UNITS[output["unit"]]
        return None

    def solve(self, pair):
        task, inputs = pair["task"], pair["inputs"]
        try:
            if task == "convert":
                asked = self._gummy(inputs["value"], inputs["unit"])
                result = asked.convert(UNITS[inputs["to_unit"]])
                # What the library itself says: the unit of the result, and
                # its name for the unit it was asked to convert from.
                return Answer({"value": float(result.x)},
                              stated={"unit": str(result.unit), "reading": asked.unit.name})
            if task == "add":
                total = self._gummy(inputs["terms"][0]["value"], inputs["terms"][0]["unit"])
                for term in inputs["terms"][1:]:
                    total = total + self._gummy(term["value"], term["unit"])
                wanted = self._wanted(pair, "value")
                if wanted is not None:
                    total = total.convert(wanted)
                return Answer({"value": float(total.x)})
            if task == "propagate":
                return self._propagate(pair)
        except self._m.IncompatibleUnitsError as exc:
            return Refusal(exc)
        if task == "type_a":
            mean = self._m.mean([float(r) for r in inputs["readings"]])
            return Answer({"mean": float(mean.x), "standard_uncertainty": float(mean.u)})
        if task == "type_b":
            return self._type_b(inputs)
        if task == "effective_dof":
            total = None
            for component in inputs["components"]:
                part = self._m.gummy(0.0, float(component["contribution"]),
                                     dof=float(component["degrees_of_freedom"]))
                total = part if total is None else total + part
            return Answer({"effective_degrees_of_freedom": float(total.dof)})
        if task == "round":
            return Unsupported("rounds when it prints a value with its uncertainty; no function "
                               "that rounds a bare number to a count of significant digits")
        return Unsupported("unknown task %r" % task)

    def _type_b(self, inputs):
        half_width = float(inputs["half_width"])
        if inputs["distribution"] == "rectangular":
            gummy = self._m.gummy(self._m.UniformDist(center=0.0, half_width=half_width))
        elif inputs["distribution"] == "triangular":
            gummy = self._m.gummy(self._m.TriangularDist(mode=0.0, half_width=half_width))
        else:
            gummy = self._m.gummy(0.0, u=half_width, p=float(inputs["coverage_probability"]))
        return Answer({"standard_uncertainty": float(gummy.u)})

    def _propagate(self, pair):
        inputs = pair["inputs"]
        names = list(inputs["variables"])
        variables = inputs["variables"]
        if inputs["covariances"]:
            index = {name: i for i, name in enumerate(names)}
            matrix = [[0.0] * len(names) for _ in names]
            for i, name in enumerate(names):
                matrix[i][i] = float(variables[name]["standard_uncertainty"]) ** 2
            for entry in inputs["covariances"]:
                i, j = (index[n] for n in entry["between"])
                product = self._m.unit(UNITS[variables[names[i]]["unit"]]) \
                    * self._m.unit(UNITS[variables[names[j]]["unit"]])
                value = self._m.gummy(float(entry["value"]), unit=UNITS[entry["unit"]])
                matrix[i][j] = matrix[j][i] = float(value.convert(product).x)
            gummys = self._m.gummy.create(
                [float(variables[n]["value"]) for n in names],
                unit=[UNITS[variables[n]["unit"]] for n in names],
                covariance_matrix=matrix)
        else:
            gummys = [self._gummy(variables[n]["value"], variables[n]["unit"],
                                  variables[n]["standard_uncertainty"]) for n in names]
        result = evaluate(inputs["model"], dict(zip(names, gummys)))
        result = result.convert(self._wanted(pair, "value"))
        return Answer({"value": float(result.x),
                       "combined_standard_uncertainty": float(result.u)})

    def close(self):
        pass
