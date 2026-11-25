"""Adapter for unyt (https://unyt.readthedocs.io), used as a library.

- `convert`, `add`: `unyt_quantity.to` and `+`.
- unyt has `degC` and `degF` for temperatures and `delta_degC`, `delta_degF`
  for differences; the adapter uses the one the pair means.
- Uncertainty and rounding: not offered; the package has units only.

The adapter does no arithmetic. Written by Claude (AI).
"""
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> the package's own unit expression.
UNITS = {
    "in": "inch", "mm": "mm", "m": "m", "s": "s", "lb": "lb", "kg": "kg",
    "km/h": "km/hr", "m/s": "m/s", "kW.h": "kW*hr", "J": "J",
    "degC": "degC", "degF": "degF", "K": "K",
    "delta_degC": "delta_degC", "delta_degF": "delta_degF",
    "V": "V", "A": "A", "W": "W", "mm^2": "mm**2",
    "ft": "ft", "mi": "mile", "mi/h": "mile/hr", "nmi": "nmi", "km": "km",
    "L": "L", "m^3": "m**3", "m^2": "m**2", "in^2": "inch**2",
    "atm": "atm", "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    # unyt's `cal` is 4.184 J.
    "cal_th": "cal", "cal": "cal",
    "min": "min", "h": "hr", "mV": "mV", "ohm": "ohm",
    "ton": "ton",
}

NO_UNIT = {
    "1": "not used by the tasks this adapter offers",
    "gal": "no unit named gallon",
    "pt": "no unit named pint",
}


class UnytAdapter:
    name = "unyt"
    units = UNITS
    no_unit = NO_UNIT

    def __init__(self):
        import unyt
        self._unyt = unyt

    def versions(self):
        from importlib.metadata import version
        return {"unyt": version("unyt"), "numpy": version("numpy")}

    def close(self):
        pass

    def solve(self, pair):
        task, inputs = pair["task"], pair["inputs"]
        if task not in ("convert", "add"):
            return Unsupported("no function for the task %r" % task)
        if task == "convert":
            spellings = [inputs["unit"], inputs["to_unit"]]
        else:
            spellings = [t["unit"] for t in inputs["terms"]]
            spellings += [o["unit"] for o in pair["reference"].get("outputs", [])]
        for spelling in spellings:
            if spelling in self.no_unit:
                return Unsupported(self.no_unit[spelling])
            if spelling not in self.units:
                return Unsupported("no unit known to the adapter for %r" % spelling)
        quantity = self._unyt.unyt_quantity
        errors = self._unyt.exceptions
        try:
            if task == "convert":
                asked = quantity(float(inputs["value"]), self.units[spellings[0]])
                result = asked.to(self.units[spellings[1]])
                return Answer({"value": float(result)},
                              stated={"unit": str(result.units), "reading": str(asked.units)})
            terms = [quantity(float(t["value"]), self.units[t["unit"]]) for t in inputs["terms"]]
            total = terms[0]
            for term in terms[1:]:
                total = total + term
            if len(spellings) > len(terms):
                total = total.to(self.units[spellings[len(terms)]])
            return Answer({"value": float(total)}, stated={"unit": str(total.units)})
        except (errors.UnitConversionError, errors.UnitOperationError) as exc:
            return Refusal(exc)
