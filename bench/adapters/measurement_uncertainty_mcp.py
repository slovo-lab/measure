"""Adapter for measurement-uncertainty-mcp
(https://github.com/kyb8801/measurement-uncertainty-mcp), a server for AI
agents that evaluates measurement uncertainty.

It is not on the Python package index; it is installed from its repository
(see requirements-adapters.txt for the commit tested) and started locally.

What is put to it:
  type_a         -> tool type_a_uncertainty
  type_b         -> tools type_b_rectangular and type_b_triangular
  effective_dof  -> tool welch_satterthwaite

What is reported as unsupported, and why:
  type_b with a normal distribution: the tool takes a coverage factor k, while
      our pairs give a coverage probability; turning one into the other would
      be the adapter doing the calculation.
  propagate: combine_uncertainty needs the sensitivity coefficients from the
      caller instead of a model, and monte_carlo_propagate takes a model but
      answers by random sampling, which is a different method from the
      first-order law our reference answers come from.
  convert, add, round: the server has no units and no such tools.

Written by Claude (AI).
"""
from fractions import Fraction

from bench.mcp_client import StdioServer
from bench.runner import Answer, Unsupported


def _f(text):
    return float(Fraction(text))


class MeasurementUncertaintyMcpAdapter:
    name = "measurement-uncertainty-mcp (server)"

    def __init__(self):
        self._server = StdioServer("measurement-uncertainty-mcp")
        self._server.start()

    def versions(self):
        from importlib.metadata import version
        return {"measurement-uncertainty-mcp": version("measurement-uncertainty-mcp"),
                "mcp": version("mcp")}

    def close(self):
        self._server.close()

    def _call(self, tool, arguments):
        is_error, payload, text = self._server.call(tool, arguments)
        if is_error or not isinstance(payload, dict):
            raise RuntimeError("server error from %s: %s" % (tool, " ".join(text.split())[:200]))
        return payload

    def solve(self, pair):
        task = pair["task"]
        inputs = pair["inputs"]
        if task == "type_a":
            got = self._call("type_a_uncertainty",
                             {"samples": [_f(r) for r in inputs["readings"]]})
            return Answer({"mean": float(got["mean"]),
                           "standard_uncertainty": float(got["standard_uncertainty"])})
        if task == "type_b":
            tools = {"rectangular": "type_b_rectangular", "triangular": "type_b_triangular"}
            if inputs["distribution"] not in tools:
                return Unsupported("type_b_normal takes a coverage factor, not the coverage "
                                   "probability given in the pair")
            got = self._call(tools[inputs["distribution"]],
                             {"half_width": _f(inputs["half_width"])})
            return Answer({"standard_uncertainty": float(got["standard_uncertainty"])})
        if task == "effective_dof":
            components = [
                {"name": "c%d" % (i + 1), "u": _f(c["contribution"]),
                 "dof": _f(c["degrees_of_freedom"])}
                for i, c in enumerate(inputs["components"])
            ]
            got = self._call("welch_satterthwaite", {"components": components})
            return Answer({"effective_degrees_of_freedom": float(got["effective_dof"])})
        if task == "propagate":
            return Unsupported("no tool for first-order propagation through a model: "
                               "combine_uncertainty needs sensitivity coefficients from the "
                               "caller, and monte_carlo_propagate uses random sampling")
        return Unsupported("no tool for the task '%s'; the server has no units" % task)
