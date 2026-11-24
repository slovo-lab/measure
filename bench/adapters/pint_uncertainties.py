"""Adapter for Pint together with the 'uncertainties' package.

Pint converts units and checks dimensions; 'uncertainties' propagates
uncertainty to first order, including covariances. Neither offers Type A or
Type B evaluation, so those tasks are reported as not offered.
Written by Claude (AI).
"""
from importlib import metadata

from ..model import evaluate
from ..numbers import to_float
from ..outcome import NotOffered, Refused

# Spellings in the pairs file that Pint writes differently.
_UNITS = {"kW.h": "kW*h"}


def _unit(text):
    return _UNITS.get(text, text)


class PintUncertainties:
    name = "Pint + uncertainties"

    def __init__(self):
        import pint
        import uncertainties

        self._pint = pint
        self._unc = uncertainties
        self._ureg = pint.UnitRegistry()

    def versions(self):
        return {name: metadata.version(name) for name in ("Pint", "uncertainties", "numpy")}

    def solve(self, pair):
        task = pair["task"]
        try:
            if task == "convert":
                return self._convert(pair)
            if task == "add":
                return self._add(pair)
            if task == "propagate":
                return self._propagate(pair)
        except self._pint.DimensionalityError as exc:
            raise Refused(str(exc)) from exc
        raise NotOffered("no %s feature in Pint or uncertainties" % task)

    def _quantity(self, value, unit):
        return self._ureg.Quantity(value, _unit(unit))

    def _convert(self, pair):
        inputs = pair["inputs"]
        out = pair["reference_units"]["value"]
        result = self._quantity(to_float(inputs["value"]), inputs["unit"]).to(_unit(inputs["to_unit"]))
        return {"value": (result.to(_unit(out)).magnitude, out)}

    def _add(self, pair):
        terms = [self._quantity(to_float(t["value"]), t["unit"]) for t in pair["inputs"]["terms"]]
        total = terms[0]
        for term in terms[1:]:
            total = total + term
        out = pair["reference_units"].get("value", pair["inputs"]["terms"][0]["unit"])
        return {"value": (total.to(_unit(out)).magnitude, out)}

    def _propagate(self, pair):
        inputs = pair["inputs"]
        names = list(inputs["variables"])
        nominal = [to_float(inputs["variables"][n]["value"]) for n in names]
        sigma = [to_float(inputs["variables"][n]["standard_uncertainty"]) for n in names]
        if inputs["covariances"]:
            # Covariances are stated in the product of the two variables' own
            # units, which the format requires, so the numbers go in as given.
            matrix = [[0.0] * len(names) for _ in names]
            for i, s in enumerate(sigma):
                matrix[i][i] = s * s
            for cov in inputs["covariances"]:
                i, j = (names.index(n) for n in cov["between"])
                matrix[i][j] = matrix[j][i] = to_float(cov["value"])
            numbers = self._unc.correlated_values(nominal, matrix)
        else:
            numbers = [self._unc.ufloat(n, s) for n, s in zip(nominal, sigma)]
        values = {
            name: self._quantity(number, inputs["variables"][name]["unit"])
            for name, number in zip(names, numbers)
        }
        result = evaluate(inputs["model"], values)
        out = pair["reference_units"]["value"]
        magnitude = result.to(_unit(out)).magnitude
        return {
            "value": (magnitude.nominal_value, out),
            "combined_standard_uncertainty": (magnitude.std_dev, out),
        }
