"""Adapter for convert-units (https://github.com/convert-units/convert-units),
a JavaScript unit converter, used as a library: `convert(1).from('in').to('mm')`.

The library has a fixed list of units per kind of quantity and converts
within one kind. It has temperatures (`C`, `F`, `K`) and no temperature
differences, no addition of quantities, no uncertainty and no rounding.

The adapter does no arithmetic. Written by Claude (AI).
"""
from bench.adapters.mathjs_adapter import MathjsAdapter
from bench.runner import Unsupported

# Spelling in the pairs file -> the library's own abbreviation.
UNITS = {
    "in": "in", "mm": "mm", "m": "m", "s": "s", "lb": "lb", "kg": "kg",
    "km/h": "km/h", "m/s": "m/s", "mi/h": "m/h", "kW.h": "kWh", "J": "J",
    "degC": "C", "degF": "F", "K": "K",
    "ft": "ft", "mi": "mi", "km": "km",
    "L": "l", "m^3": "m3", "m^2": "m2", "in^2": "in2", "mm^2": "mm2",
    "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    "min": "min", "h": "h",
    "V": "V", "A": "A", "W": "W", "mV": "mV",
    # Bare words, for the questions that do not say which reading is meant.
    "gal": "gal", "pt": "pnt", "ton": "t",
}

NO_UNIT = {
    "nmi": "no unit for the nautical mile",
    "atm": "no unit for the standard atmosphere",
    "cal_th": "no unit for the calorie", "cal": "no unit for the calorie",
    "delta_degF": "no separate unit for a temperature difference",
    "delta_degC": "no separate unit for a temperature difference",
    "ohm": "no unit for the ohm",
    "1": "not used by the tasks this adapter offers",
}

REFUSALS = ("Cannot convert incompatible measures",)


class ConvertUnitsAdapter(MathjsAdapter):
    name = "convert-units"
    library = "convert-units"
    units = UNITS
    no_unit = NO_UNIT
    refusals = REFUSALS

    def solve(self, pair):
        if pair["task"] == "add":
            return Unsupported("no function for adding quantities")
        return super().solve(pair)
