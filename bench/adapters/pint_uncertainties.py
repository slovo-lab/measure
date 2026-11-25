"""Adapter for Pint together with the `uncertainties` package.

Pint converts units and checks dimensions. `uncertainties` propagates standard
uncertainties to first order, with correlations. Neither has a function for a
Type A or Type B evaluation, so those tasks are reported as unsupported; the
adapter does not do the statistics itself.

Numbers from the pair are handed over as Python floats, which is how these
libraries are normally used.

Written by Claude (AI).
"""
from bench.model import evaluate
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> spelling Pint understands.
UNITS = {
    "in": "inch", "mm": "millimeter", "m": "meter", "s": "second",
    "lb": "pound", "kg": "kilogram",
    "km/h": "kilometer / hour", "m/s": "meter / second",
    "kW.h": "kilowatt * hour", "J": "joule",
    "degC": "degC", "degF": "degF", "K": "kelvin",
    "V": "volt", "A": "ampere", "W": "watt",
    "mm^2": "millimeter ** 2",
    "ft": "foot", "mi": "mile", "mi/h": "mile / hour", "nmi": "nautical_mile",
    "km": "kilometer", "L": "liter", "m^3": "meter ** 3", "m^2": "meter ** 2",
    "in^2": "inch ** 2",
    "atm": "standard_atmosphere", "kPa": "kilopascal", "bar": "bar", "Pa": "pascal",
    "cal_th": "thermochemical_calorie",
    # The bare word, for the question that does not say which calorie is meant.
    "cal": "cal",
    "min": "minute", "h": "hour",
    "mV": "millivolt", "ohm": "ohm",
    # Pint has separate units for temperature differences.
    "delta_degF": "delta_degF", "delta_degC": "delta_degC",
    "1": "dimensionless",
}


class PintUncertaintiesAdapter:
    name = "Pint + uncertainties"

    def __init__(self):
        import pint
        import uncertainties
        self._pint = pint
        self._uncertainties = uncertainties
        self._ureg = pint.UnitRegistry()

    def versions(self):
        import numpy
        return {"pint": self._pint.__version__,
                "uncertainties": self._uncertainties.__version__,
                "numpy": numpy.__version__}

    def _unit(self, spelling):
        return self._ureg.Unit(UNITS[spelling])

    def _reference_unit(self, pair, name):
        if "outputs" not in pair["reference"]:
            return None
        for output in pair["reference"]["outputs"]:
            if output["name"] == name:
                return self._unit(output["unit"])
        return None

    def solve(self, pair):
        task = pair["task"]
        if task == "convert":
            return self._convert(pair["inputs"])
        if task == "add":
            return self._add(pair)
        if task == "propagate":
            return self._propagate(pair)
        if task == "type_a":
            return Unsupported("no function for a Type A evaluation in Pint or uncertainties")
        if task == "type_b":
            return Unsupported("no function for a Type B evaluation in Pint or uncertainties")
        if task == "effective_dof":
            return Unsupported("no function for effective degrees of freedom "
                               "in Pint or uncertainties")
        if task == "round":
            return Unsupported("no function that rounds to a number of significant digits; "
                               "Python's round() on a quantity counts decimal places")
        return Unsupported("unknown task %r" % task)

    def _convert(self, inputs):
        quantity = self._ureg.Quantity(float(inputs["value"]), self._unit(inputs["unit"]))
        try:
            converted = quantity.to(self._unit(inputs["to_unit"]))
        except self._pint.DimensionalityError as exc:
            return Refusal(exc)
        # What Pint itself says: the unit of the result, and the name it gave
        # the unit it was asked to convert from.
        return Answer({"value": float(converted.magnitude)},
                      stated={"unit": "{:~}".format(converted.units),
                              "reading": str(quantity.units)})

    def _add(self, pair):
        terms = [self._ureg.Quantity(float(t["value"]), self._unit(t["unit"]))
                 for t in pair["inputs"]["terms"]]
        try:
            total = terms[0]
            for term in terms[1:]:
                total = total + term
        except self._pint.DimensionalityError as exc:
            return Refusal(exc)
        unit = self._reference_unit(pair, "value") or total.units
        return Answer({"value": float(total.to(unit).magnitude)})

    def _propagate(self, pair):
        inputs = pair["inputs"]
        names = list(inputs["variables"])
        index = {name: i for i, name in enumerate(names)}
        units = [self._unit(inputs["variables"][n]["unit"]) for n in names]
        values = [float(inputs["variables"][n]["value"]) for n in names]
        sigmas = [float(inputs["variables"][n]["standard_uncertainty"]) for n in names]
        covariance = [[0.0] * len(names) for _ in names]
        for i, sigma in enumerate(sigmas):
            covariance[i][i] = sigma ** 2
        for entry in inputs["covariances"]:
            i, j = (index[n] for n in entry["between"])
            # The covariance is converted to the product of the two variables' units.
            value = self._ureg.Quantity(float(entry["value"]), self._unit(entry["unit"]))
            value = float(value.to(units[i] * units[j]).magnitude)
            covariance[i][j] = covariance[j][i] = value
        if inputs["covariances"]:
            numbers = self._uncertainties.correlated_values(values, covariance)
        else:
            numbers = [self._uncertainties.ufloat(v, s) for v, s in zip(values, sigmas)]
        variables = {name: self._ureg.Quantity(number, unit)
                     for name, number, unit in zip(names, numbers, units)}
        try:
            result = evaluate(inputs["model"], variables)
            result = result.to(self._reference_unit(pair, "value"))
        except self._pint.DimensionalityError as exc:
            return Refusal(exc)
        magnitude = result.magnitude
        return Answer({"value": float(magnitude.nominal_value),
                       "combined_standard_uncertainty": float(magnitude.std_dev)})
