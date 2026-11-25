"""Adapter for mathjs (https://mathjs.org), a JavaScript library, used as a library.

mathjs has units: `math.unit(1, 'inch').to('mm')`. Agents reach it through
calculator servers and through code they write themselves.

- `convert`, `add`: the library's own `to` and `add`.
- Everything about uncertainty, and rounding to significant digits by the
  rule in the pairs: unsupported; the library has units, not uncertainty.

The adapter does no arithmetic. Numbers from the pair are handed over as
JavaScript numbers. Written by Claude (AI).
"""
from bench.node_client import ask, library_version
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> the library's own unit name.
UNITS = {
    "in": "inch", "mm": "mm", "m": "m", "s": "s", "lb": "lb", "kg": "kg",
    "km/h": "km/h", "m/s": "m/s", "kW.h": "kWh", "J": "J",
    "degC": "degC", "degF": "degF", "K": "K",
    "V": "V", "A": "A", "W": "W", "mm^2": "mm^2",
    "ft": "ft", "mi": "mi", "mi/h": "mi/h", "km": "km",
    "L": "L", "m^3": "m^3", "m^2": "m^2", "in^2": "in^2",
    "atm": "atm", "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    "min": "min", "h": "h", "mV": "mV", "ohm": "ohm",
}

# Spellings for which the library has no unit.
NO_UNIT = {
    "nmi": "no unit for the nautical mile",
    "cal_th": "no unit for the calorie",
    "cal": "no unit for the calorie",
    "delta_degF": "no separate unit for a temperature difference",
    "delta_degC": "no separate unit for a temperature difference",
    "1": "not used by the tasks this adapter offers",
}

REFUSALS = ("Units do not match",)


class MathjsAdapter:
    name = "mathjs"
    library = "mathjs"
    units = UNITS
    no_unit = NO_UNIT
    refusals = REFUSALS

    def __init__(self):
        self._versions = library_version(self.library)

    def versions(self):
        return dict(self._versions)

    def close(self):
        pass

    def _names(self, pair, spellings):
        return [self.units[s] for s in spellings]

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
        names = self._names(pair, spellings)
        if task == "convert":
            request = {"op": "convert", "value": float(inputs["value"]),
                       "unit": names[0], "to_unit": names[1]}
        else:
            count = len(inputs["terms"])
            request = {"op": "add", "terms": [
                {"value": float(t["value"]), "unit": name}
                for t, name in zip(inputs["terms"], names[:count])]}
            if len(names) > count:
                request["want_unit"] = names[count]
        request["library"] = self.library
        reply = ask(request)
        if not reply.get("ok"):
            message = reply.get("error", "")
            if any(marker in message for marker in self.refusals):
                return Refusal(message)
            raise RuntimeError("the library answered with an error: %s" % message[:300])
        stated = {"unit": reply.get("unit")} if reply.get("unit") else {}
        return Answer({"value": float(reply["value"])}, stated=stated)
