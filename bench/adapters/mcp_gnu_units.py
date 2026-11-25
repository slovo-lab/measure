"""Adapter for mcp-gnu-units (https://pypi.org/project/mcp-gnu-units/), a
server for AI agents built on the GNU units database.

Its `convert` tool takes two expressions in GNU units syntax, so the adapter
writes the question in that syntax: `26.2 mile` to `km`. Temperatures use the
database's functions, `tempC(25)`, and temperature differences use its
interval units, `degC` and `degF`. The server has no tool for adding
quantities or for uncertainty.

The server installs next to the other tools (requirements-adapters.txt). If it
is kept somewhere else, name it through the variable
MEASURE_SERVER_MCP_GNU_UNITS.

Written by Claude (AI).
"""
from fractions import Fraction

from bench.mcp_client import StdioServer
from bench.runner import Answer, Refusal, Unsupported

# Spelling in the pairs file -> name in the GNU units database.
UNITS = {
    "in": "inch", "mm": "mm", "m": "m", "km": "km", "ft": "ft", "mi": "mile",
    "nmi": "nauticalmile",
    "lb": "pound", "kg": "kg",
    "km/h": "km/hour", "m/s": "m/s", "mi/h": "mile/hour",
    "kW.h": "kW*hour", "J": "joule", "cal_th": "calorie_th",
    "L": "liter", "m^3": "m^3", "m^2": "m^2", "in^2": "in^2", "mm^2": "mm^2",
    "atm": "atm", "kPa": "kPa", "bar": "bar", "Pa": "Pa",
    "min": "min", "h": "hour", "s": "s",
    "K": "K",
    # Temperature differences are plain units in this database.
    "delta_degC": "degC", "delta_degF": "degF",
}

# Temperatures (not differences) are functions in this database.
TEMPERATURE = {"degC": "tempC", "degF": "tempF"}


def _number(text):
    """The number as the pair writes it, when that is a plain decimal."""
    try:
        float(text)
        return text
    except ValueError:
        return repr(float(Fraction(text)))


class McpGnuUnitsAdapter:
    name = "mcp-gnu-units (server)"

    def __init__(self):
        self._server = StdioServer("mcp-gnu-units")
        self._server.start()
        self._info = None

    def versions(self):
        if self._info is None:
            _, payload, _ = self._server.call("info", {})
            self._info = payload if isinstance(payload, dict) else {}
        database = self._info.get("units_db", {})
        return {"mcp-gnu-units": str(self._info.get("version", "unknown")),
                "GNU units data": str(database.get("data_version", "unknown"))}

    def close(self):
        self._server.close()

    def solve(self, pair):
        if pair["task"] != "convert":
            return Unsupported("no tool for the task '%s'; the server converts and "
                               "looks up units" % pair["task"])
        inputs = pair["inputs"]
        unit, target, value = inputs["unit"], inputs["to_unit"], _number(inputs["value"])
        if unit in TEMPERATURE:
            from_expr = "%s(%s)" % (TEMPERATURE[unit], value)
        elif unit in UNITS:
            from_expr = "%s %s" % (value, UNITS[unit])
        else:
            return Unsupported("no name for '%s' in the adapter's table" % unit)
        to_expr = TEMPERATURE.get(target) or UNITS.get(target)
        if to_expr is None:
            return Unsupported("no name for '%s' in the adapter's table" % target)
        is_error, payload, text = self._server.call("convert",
                                                    {"from_expr": from_expr, "to_expr": to_expr})
        flat = " ".join(text.split())
        if is_error:
            if "non-conformable" in flat:
                return Refusal(flat[:200])
            raise RuntimeError("server error: %s" % flat[:200])
        if not isinstance(payload, dict) or "value" not in payload:
            raise RuntimeError("unreadable answer from the server: %r" % flat[:200])
        return Answer({"value": float(payload["value"])})
