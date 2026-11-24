"""Adapter for ucon's server for AI agents (`ucon-mcp`, from the ucon-tools package).

This is the same engine as `ucon_adapter.py` tests, reached the way an AI
agent reaches it: through the server's `convert` tool. In ucon-tools 0.13.0
we found no tool that adds two quantities or that propagates an uncertainty
through a model given as a formula, so only conversions are put to it; the
other tasks are reported as unsupported.

Written by Claude (AI).
"""
from fractions import Fraction

from bench.adapters.ucon_adapter import NO_UNIT, UNITS, units_used
from bench.mcp_client import StdioServer
from bench.runner import Answer, Refusal, Unsupported


class UconMcpAdapter:
    name = "ucon-mcp (server)"

    def __init__(self):
        self._server = StdioServer("ucon-mcp")
        self._server.start()

    def versions(self):
        from importlib.metadata import version
        return {"ucon-tools": version("ucon-tools"), "ucon": version("ucon"),
                "mcp": version("mcp")}

    def close(self):
        self._server.close()

    def solve(self, pair):
        if pair["task"] != "convert":
            return Unsupported("no tool for the task '%s'; the server's tools convert, "
                               "and multiply or divide by factors" % pair["task"])
        for unit in units_used(pair):
            if unit in NO_UNIT:
                return Unsupported(NO_UNIT[unit])
        inputs = pair["inputs"]
        is_error, payload, text = self._server.call("convert", {
            "value": float(Fraction(inputs["value"])),
            "from_unit": UNITS[inputs["unit"]],
            "to_unit": UNITS[inputs["to_unit"]],
        })
        if not isinstance(payload, dict):
            raise RuntimeError("unreadable answer from the server: %r" % text[:200])
        if "error" in payload:
            if payload.get("error_type") == "dimension_mismatch":
                return Refusal(payload["error"])
            raise RuntimeError("server error: %s" % payload["error"])
        if is_error:
            raise RuntimeError("server error: %s" % text[:200])
        return Answer({"value": float(payload["quantity"])})
