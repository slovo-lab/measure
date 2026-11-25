"""Adapter for astropy.units (https://docs.astropy.org/en/stable/units/), used as a library.

- `convert`, `add`: `Quantity.to` and `+`.
- Temperatures: astropy's documentation says that converting between degrees
  Celsius, degrees Fahrenheit and kelvin needs the equivalency
  `astropy.units.temperature()`; without it the conversion is refused. The
  adapter passes that equivalency when both units of a pair are temperatures,
  as the documentation tells a user to do. The package has no separate unit
  for a temperature difference, so those pairs are not offered.
- Uncertainty and rounding: not offered. (`astropy.uncertainty` works with
  sampled distributions, which is a different method from the one the pairs
  ask about.)

Non-metric units live in `astropy.units.imperial`, the atmosphere in
`astropy.units.cds`. The adapter does no arithmetic. Written by Claude (AI).
"""
from bench.runner import Answer, Refusal, Unsupported

TEMPERATURES = ("degC", "degF", "K")

NO_UNIT = {
    "delta_degF": "no separate unit for a temperature difference",
    "delta_degC": "no separate unit for a temperature difference",
    "1": "not used by the tasks this adapter offers",
}


def _units():
    import astropy.units as u
    from astropy.units import cds, imperial
    return {
        "in": imperial.inch, "mm": u.mm, "m": u.m, "s": u.s, "lb": imperial.lb, "kg": u.kg,
        "km/h": u.km / u.h, "m/s": u.m / u.s, "kW.h": u.kW * u.h, "J": u.J,
        "degC": u.deg_C, "degF": imperial.deg_F, "K": u.K,
        "V": u.V, "A": u.A, "W": u.W, "mm^2": u.mm ** 2,
        "ft": imperial.ft, "mi": imperial.mi, "mi/h": imperial.mi / u.h,
        "nmi": imperial.nmi, "km": u.km,
        "L": u.l, "m^3": u.m ** 3, "m^2": u.m ** 2, "in^2": imperial.inch ** 2,
        "atm": cds.atm, "kPa": u.kPa, "bar": u.bar, "Pa": u.Pa,
        # astropy's `cal` is 4.184 J.
        "cal_th": imperial.cal, "cal": imperial.cal,
        "min": u.min, "h": u.h, "mV": u.mV, "ohm": u.ohm,
        # Bare words, for the questions that do not say which reading is meant.
        "gal": imperial.gallon, "pt": imperial.pint, "ton": imperial.ton,
    }


class AstropyAdapter:
    name = "astropy.units"

    def __init__(self):
        import astropy.units as u
        self._u = u
        self.units = _units()
        self.no_unit = NO_UNIT

    def versions(self):
        from importlib.metadata import version
        return {"astropy": version("astropy"), "numpy": version("numpy")}

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
        u = self._u
        try:
            if task == "convert":
                asked = float(inputs["value"]) * self.units[spellings[0]]
                target = self.units[spellings[1]]
                if all(s in TEMPERATURES for s in spellings):
                    result = asked.to(target, equivalencies=u.temperature())
                else:
                    result = asked.to(target)
                return Answer({"value": float(result.value)},
                              stated={"unit": str(result.unit), "reading": str(asked.unit)})
            terms = [float(t["value"]) * self.units[t["unit"]] for t in inputs["terms"]]
            total = terms[0]
            for term in terms[1:]:
                total = total + term
            if len(spellings) > len(terms):
                total = total.to(self.units[spellings[len(terms)]])
            return Answer({"value": float(total.value)}, stated={"unit": str(total.unit)})
        except u.UnitConversionError as exc:
            return Refusal(exc)
