"""Adapter for mcp-units (https://github.com/quantumleeps/mcp-units), a server
for AI agents that converts units with the Pint library.

It is not on the Python package index; it is installed from its repository
(see requirements-adapters.txt for the commit tested). Only its `convert`
tool is used. It has no tool for adding quantities or for uncertainty.

Written by Claude (AI).
"""
from fractions import Fraction

from bench.adapters.pint_uncertainties import UNITS
from bench.mcp_client import StdioServer
from bench.runner import Answer, Refusal, Unsupported


class McpUnitsAdapter:
    name = "mcp-units (server)"

    def __init__(self):
        self._server = StdioServer("mcp-units")
        self._server.start()

    def versions(self):
        from importlib.metadata import version
        return {"mcp-units": version("mcp-units"), "pint": version("pint"),
                "mcp": version("mcp")}

    def close(self):
        self._server.close()

    def solve(self, pair):
        if pair["task"] != "convert":
            return Unsupported("no tool for the task '%s'; the server converts, parses "
                               "and simplifies units" % pair["task"])
        inputs = pair["inputs"]
        is_error, payload, text = self._server.call("convert", {
            "value": float(Fraction(inputs["value"])),
            "from_unit": UNITS[inputs["unit"]],
            "to_unit": UNITS[inputs["to_unit"]],
        })
        flat = " ".join(text.split())
        if is_error or not isinstance(payload, dict) or "output_value" not in payload:
            if "dimension" in flat.lower() or "cannot convert" in flat.lower():
                return Refusal(flat[:200])
            raise RuntimeError("server error: %s" % flat[:200])
        # What the server itself says: its names for the two units.
        return Answer({"value": float(payload["output_value"])},
                      stated={"unit": payload.get("output_unit"),
                              "reading": payload.get("input_unit")})
