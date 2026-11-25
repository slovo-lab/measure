"""Adapter for p6plab-mcp-calculator (https://pypi.org/project/p6plab-mcp-calculator/).

A calculator server for AI agents with 70 tools. Two of them bear on the
pairs:

- `round` rounds a number to a count of decimal places. The pairs ask for a
  count of significant digits; the adapter restates that as decimal places
  from the position of the first digit of the number as written in the pair
  (for 2.675 and three significant digits: two decimal places). That is the
  only thing the adapter works out, and it concerns the question, not the
  answer.
- `convert_units` exists, but in the version tested it answers every request
  with the text "Unit conversion not yet implemented" and no number. The
  adapter calls it, and reports the pair as not offered, quoting the server.

The server has `mean` and `std_dev` but no tool that gives the standard
uncertainty of a mean, so Type A pairs are not offered either.

Written by Claude (AI).
"""
from decimal import Decimal

from bench.mcp_client import StdioServer
from bench.runner import Answer, Unsupported

# Spelling in the pairs file -> a name the server's own unit list uses.
UNITS = {"in": "inch", "mm": "millimeter", "m": "meter", "ft": "foot", "km": "kilometer"}


def decimal_places(written, significant_digits):
    """Decimal places that keep `significant_digits` digits of the number as written."""
    return significant_digits - 1 - Decimal(written).adjusted()


def _innermost(payload):
    while isinstance(payload, dict) and "result" in payload:
        payload = payload["result"]
    return payload


class P6plabCalculatorAdapter:
    name = "p6plab-mcp-calculator (server)"

    def __init__(self):
        self._server = StdioServer("p6plab-mcp-calculator")
        self._server.start()

    def versions(self):
        from importlib.metadata import version
        return {"p6plab-mcp-calculator": version("p6plab-mcp-calculator"),
                "mcp": version("mcp")}

    def close(self):
        self._server.close()

    def _call(self, tool, params):
        is_error, payload, text = self._server.call(tool, {"params": params})
        if is_error:
            raise RuntimeError("server error: %s" % " ".join(text.split())[:300])
        return _innermost(payload), text

    def solve(self, pair):
        task, inputs = pair["task"], pair["inputs"]
        if task == "round":
            places = decimal_places(inputs["value"], inputs["significant_digits"])
            if places < 0:
                return Unsupported("the tool rounds to decimal places only")
            answer, text = self._call("round", {"number": float(inputs["value"]),
                                                "decimals": places})
            if not isinstance(answer, (int, float)):
                raise RuntimeError("unreadable answer from the server: %r" % text[:200])
            return Answer({"value": float(answer)})
        if task == "convert":
            answer, text = self._call("convert_units", {
                "value": float(inputs["value"]),
                "from_unit": UNITS.get(inputs["unit"], inputs["unit"]),
                "to_unit": UNITS.get(inputs["to_unit"], inputs["to_unit"])})
            if isinstance(answer, str):
                return Unsupported("the tool `convert_units` answered: %r" % answer)
            raise RuntimeError("the server now answers conversions; the adapter "
                               "must be rewritten: %r" % text[:200])
        return Unsupported("no tool for the task %r" % task)
