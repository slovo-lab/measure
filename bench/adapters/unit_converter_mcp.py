"""Adapter for unit-converter-mcp (https://pypi.org/project/unit-converter-mcp/).

A server for AI agents with one conversion tool per kind of quantity
(`convert_length`, `convert_mass`, ...). Each tool accepts a fixed list of
unit names. The adapter picks the tool that belongs to the unit being
converted from and passes the names from the server's own lists.

The server has no tool for adding quantities or for uncertainty, so those
tasks are reported as unsupported.

Written by Claude (AI).
"""
from fractions import Fraction

from bench.mcp_client import StdioServer
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> (tool, unit name in that tool's list).
UNITS = {
    "in": ("convert_length", "inch"), "mm": ("convert_length", "millimeter"),
    "m": ("convert_length", "meter"), "km": ("convert_length", "kilometer"),
    "ft": ("convert_length", "foot"), "mi": ("convert_length", "mile"),
    "nmi": ("convert_length", "nautical mile"),
    "lb": ("convert_mass", "pound"), "kg": ("convert_mass", "kilogram"),
    "km/h": ("convert_speed", "kilometers per hour"),
    "m/s": ("convert_speed", "meters per second"),
    "mi/h": ("convert_speed", "miles per hour"),
    "kW.h": ("convert_energy", "kilowatt hour"), "J": ("convert_energy", "joule"),
    # The server's "calorie" is 4.184 J, the thermochemical calorie.
    "cal_th": ("convert_energy", "calorie"),
    "degC": ("convert_temperature", "celsius"),
    "degF": ("convert_temperature", "fahrenheit"),
    "K": ("convert_temperature", "kelvin"),
    "L": ("convert_volume", "liter"), "m^3": ("convert_volume", "cubic meter"),
    "atm": ("convert_pressure", "atmosphere"), "kPa": ("convert_pressure", "kilopascal"),
    "bar": ("convert_pressure", "bar"), "Pa": ("convert_pressure", "pascal"),
    "in^2": ("convert_area", "square inch"), "mm^2": ("convert_area", "square millimeter"),
    "m^2": ("convert_area", "square meter"),
    "min": ("convert_time", "minutes"), "h": ("convert_time", "hours"),
    "s": ("convert_time", "seconds"),
    # Bare words, for the questions that do not say which reading is meant.
    "cal": ("convert_energy", "calorie"), "gal": ("convert_volume", "gallon"),
    "pt": ("convert_volume", "pint"), "ton": ("convert_mass", "ton"),
}

# Spellings for which the server's lists have no unit.
NO_UNIT = {
    "delta_degF": "the temperature tool converts temperatures only, not temperature differences",
    "delta_degC": "the temperature tool converts temperatures only, not temperature differences",
}


class UnitConverterMcpAdapter:
    name = "unit-converter-mcp (server)"

    def __init__(self):
        self._server = StdioServer("unit-converter-mcp")
        self._server.start()

    def versions(self):
        from importlib.metadata import version
        return {"unit-converter-mcp": version("unit-converter-mcp"), "mcp": version("mcp")}

    def close(self):
        self._server.close()

    def solve(self, pair):
        if pair["task"] != "convert":
            return Unsupported("no tool for the task '%s'; every tool of this server "
                               "converts one value between two units" % pair["task"])
        inputs = pair["inputs"]
        for unit in (inputs["unit"], inputs["to_unit"]):
            if unit in NO_UNIT:
                return Unsupported(NO_UNIT[unit])
            if unit not in UNITS:
                return Unsupported("no unit for '%s' in the server's lists" % unit)
        tool, from_name = UNITS[inputs["unit"]]
        target_tool, to_name = UNITS[inputs["to_unit"]]
        is_error, payload, text = self._server.call(tool, {
            "value": float(Fraction(inputs["value"])),
            "from_unit": from_name,
            "to_unit": to_name,
        })
        if is_error:
            if "Input should be" in text:
                # The tool has a fixed list of unit names and turned the word
                # down, naming the ones it accepts.
                return Refusal(" ".join(text.split())[:400])
            if tool != target_tool:
                # The tool for one kind of quantity was offered a unit of
                # another kind and turned the request down.
                return Refusal(" ".join(text.split())[:200])
            raise RuntimeError("server error: %s" % text[:300])
        if not isinstance(payload, dict) or "converted_value" not in payload:
            raise RuntimeError("unreadable answer from the server: %r" % text[:200])
        # What the server itself says: its names for the two units.
        return Answer({"value": float(payload["converted_value"])},
                      stated={"unit": payload.get("converted_unit"),
                              "reading": payload.get("original_unit")})
