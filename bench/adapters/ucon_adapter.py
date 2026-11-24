"""Adapter for ucon.

ucon converts units, checks dimensions, and carries one uncertainty on each
number. It has no way to state a covariance between two inputs, and no Type A
or Type B evaluation, so those are reported as not offered.
Written by Claude (AI).
"""
from importlib import metadata

from ..model import evaluate
from ..numbers import to_float
from ..outcome import NotOffered, Refused

# Spellings in the pairs file that ucon writes differently. ucon reads "nmi"
# as nano-mile (prefix n + mi), so the nautical mile is given by its full name.
_UNITS = {"kW.h": "kW*h", "nmi": "nautical_mile"}


def _unit(text):
    return _UNITS.get(text, text)


class Ucon:
    name = "ucon"

    def __init__(self):
        import ucon

        self._ucon = ucon

    def versions(self):
        return {"ucon": metadata.version("ucon")}

    def _refusals(self):
        return (self._ucon.DimensionMismatch, self._ucon.KindMismatch)

    def solve(self, pair):
        task = pair["task"]
        if task not in ("convert", "add", "propagate"):
            raise NotOffered("no %s feature in ucon" % task)
        if task == "propagate" and pair["inputs"]["covariances"]:
            raise NotOffered("ucon has no input for covariance")
        try:
            return getattr(self, "_" + task)(pair)
        except self._refusals() as exc:
            raise Refused(str(exc)) from exc
        except TypeError as exc:
            # ucon reports adding numbers of different dimensions as a
            # TypeError with this wording. Any other TypeError is a real error.
            if "different dimensions" in str(exc):
                raise Refused(str(exc)) from exc
            raise

    def _number(self, value, unit, uncertainty=None):
        return self._ucon.Number(value, self._ucon.parse_unit(_unit(unit)), uncertainty=uncertainty)

    def _convert(self, pair):
        inputs = pair["inputs"]
        out = pair["reference_units"]["value"]
        result = self._number(to_float(inputs["value"]), inputs["unit"]).to(_unit(inputs["to_unit"]))
        return {"value": (result.to(_unit(out)).quantity, out)}

    def _add(self, pair):
        terms = [self._number(to_float(t["value"]), t["unit"]) for t in pair["inputs"]["terms"]]
        total = terms[0]
        for term in terms[1:]:
            total = total + term
        out = pair["reference_units"].get("value", pair["inputs"]["terms"][0]["unit"])
        return {"value": (total.to(_unit(out)).quantity, out)}

    def _propagate(self, pair):
        inputs = pair["inputs"]
        values = {
            name: self._number(to_float(var["value"]), var["unit"],
                               uncertainty=to_float(var["standard_uncertainty"]))
            for name, var in inputs["variables"].items()
        }
        result = evaluate(inputs["model"], values)
        out = pair["reference_units"]["value"]
        result = result.to(_unit(out))
        return {
            "value": (result.quantity, out),
            "combined_standard_uncertainty": (result.uncertainty, out),
        }
