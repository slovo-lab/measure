"""Adapter for js-quantities (https://github.com/gentooboontoo/js-quantities),
a JavaScript library for quantities with units, used as a library.

The library keeps temperatures and temperature differences apart by name:
`tempC`, `tempF`, `tempK` are temperatures, `degC`, `degF`, `degK` are
differences. The adapter uses the name that means what the pair means.

- `convert`, `add`: the library's own `to` and `add`.
- Everything about uncertainty, and rounding: unsupported.

The adapter does no arithmetic. Written by Claude (AI).
"""
from bench.adapters.mathjs_adapter import MathjsAdapter

# Spelling in the pairs file -> the library's own unit name.
UNITS = {
    "in": "in", "mm": "mm", "m": "m", "s": "s", "lb": "lb", "kg": "kg",
    "km/h": "km/h", "m/s": "m/s", "kW.h": "kWh", "J": "J",
    "degC": "tempC", "degF": "tempF", "K": "tempK",
    "delta_degC": "degC", "delta_degF": "degF",
    "V": "V", "A": "A", "W": "W", "mm^2": "mm^2",
    "ft": "ft", "mi": "mi", "mi/h": "mi/h", "nmi": "nmi", "km": "km",
    "L": "l", "m^3": "m^3", "m^2": "m^2", "in^2": "in^2",
    "atm": "atm", "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    # The library's "cal" is 4.184 J, the thermochemical calorie.
    "cal_th": "cal", "cal": "cal",
    "gal": "gallon", "pt": "pint", "ton": "ton",
    "min": "min", "h": "h", "mV": "mV", "ohm": "ohm",
}

NO_UNIT = {"1": "not used by the tasks this adapter offers"}

REFUSALS = ("Incompatible units",)

DIFFERENCES = ("delta_degC", "delta_degF")


class JsQuantitiesAdapter(MathjsAdapter):
    name = "js-quantities"
    library = "js-quantities"
    units = UNITS
    no_unit = NO_UNIT
    refusals = REFUSALS

    def _names(self, pair, spellings):
        # A kelvin that stands next to a temperature difference is itself a
        # difference: the library's name for that is degK, not tempK.
        difference = any(s in DIFFERENCES for s in spellings)
        return ["degK" if (s == "K" and difference) else self.units[s] for s in spellings]
