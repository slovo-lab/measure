"""Adapter for Suncal (https://suncal.sandia.gov), the uncertainty calculator
from the Primary Standards Laboratory at Sandia National Laboratories, used
through its Python interface.

- `propagate`: a `suncal.Model` built from the pair's formula; each variable
  gets its value and a Type B standard uncertainty; `calculate_gum()` gives the
  value and the combined standard uncertainty.
- `type_a`: the readings are handed to a variable; Suncal gives the mean and
  the standard uncertainty of the mean.
- `type_b`: a variable with one Type B component of the named distribution.
- `effective_dof`: a sum of variables, each with its contribution and degrees
  of freedom; Suncal reports the effective degrees of freedom.
- `convert`, `add`, `round`: not offered. Suncal uses the Pint library for
  units and has no conversion function of its own.

Two restatements of the question, neither touching the answer: Suncal takes a
correlation coefficient where the pairs give a covariance, so the adapter
divides the covariance by the two standard uncertainties; and Suncal's uniform
and triangular distributions take the half-width under the name `a`.

Written by Claude (AI).
"""
from bench.adapters.pint_uncertainties import UNITS
from bench.runner import Answer, Unsupported


class SuncalAdapter:
    name = "Suncal"

    def __init__(self):
        import suncal
        self._suncal = suncal

    def versions(self):
        from importlib.metadata import version
        return {"suncal": version("suncal"), "pint": version("pint"),
                "sympy": version("sympy"), "numpy": version("numpy")}

    def close(self):
        pass

    def solve(self, pair):
        task = pair["task"]
        if task == "propagate":
            return self._propagate(pair)
        if task == "type_a":
            return self._type_a(pair["inputs"])
        if task == "type_b":
            return self._type_b(pair["inputs"])
        if task == "effective_dof":
            return self._effective_dof(pair["inputs"])
        return Unsupported("no function for the task %r; Suncal evaluates uncertainty "
                           "and leaves units to the Pint library" % task)

    def _propagate(self, pair):
        inputs = pair["inputs"]
        model = self._suncal.Model("f = " + inputs["model"])
        for name, v in inputs["variables"].items():
            model.var(name).measure(float(v["value"]), units=UNITS[v["unit"]]).typeb(
                unc=float(v["standard_uncertainty"]))
        for covariance in inputs["covariances"]:
            first, second = covariance["between"]
            coefficient = float(covariance["value"]) / (
                float(inputs["variables"][first]["standard_uncertainty"])
                * float(inputs["variables"][second]["standard_uncertainty"]))
            model.variables.correlate(first, second, coefficient)
        result = model.calculate_gum()
        wanted = {o["name"]: UNITS[o["unit"]] for o in pair["reference"]["outputs"]}
        result.units(f=wanted["value"])
        return Answer({
            "value": float(result.expected["f"].magnitude),
            "combined_standard_uncertainty": float(result.uncertainty["f"].magnitude)})

    def _type_a(self, inputs):
        import numpy
        model = self._suncal.Model("f = a")
        variable = model.var("a")
        variable.measure(numpy.array([float(r) for r in inputs["readings"]]),
                         units=UNITS[inputs["unit"]], autocor=False)
        return Answer({"mean": float(variable.expected.magnitude),
                       "standard_uncertainty": float(variable.uncertainty.magnitude)})

    def _type_b(self, inputs):
        half_width = float(inputs["half_width"])
        distribution = inputs["distribution"]
        if distribution == "rectangular":
            arguments = {"dist": "uniform", "a": half_width}
        elif distribution == "triangular":
            arguments = {"dist": "triangular", "a": half_width}
        elif distribution == "normal":
            arguments = {"dist": "normal", "unc": half_width,
                         "conf": float(inputs["coverage_probability"])}
        else:
            return Unsupported("no distribution known to the adapter for %r" % distribution)
        model = self._suncal.Model("f = a")
        variable = model.var("a")
        variable.measure(0.0).typeb(**arguments)
        uncertainty = variable.uncertainty
        return Answer({"standard_uncertainty": float(getattr(uncertainty, "magnitude",
                                                             uncertainty))})

    def _effective_dof(self, inputs):
        names = ["c%d" % i for i in range(len(inputs["components"]))]
        model = self._suncal.Model("f = " + " + ".join(names))
        for name, component in zip(names, inputs["components"]):
            model.var(name).measure(0.0).typeb(unc=float(component["contribution"]),
                                               degf=float(component["degrees_of_freedom"]))
        result = model.calculate_gum()
        return Answer({"effective_degrees_of_freedom": float(result.degf["f"])})
