"""Put every reference pair to a tool and compare the answers.

Statuses for one pair and one tool:
  pass         every output is within the pair's tolerance, or the tool
               refused a task that must be refused
  fail         an output is outside the tolerance, or the tool returned a
               number for a task that must be refused
  refused      the tool refused a task that has a valid answer
  error        the tool raised an error that is not a refusal
  not_offered  the tool has no feature for this kind of task

Written by Claude (AI).
"""
import json
import math
from fractions import Fraction

from .numbers import to_fraction
from .outcome import NotOffered, Refused

STATUSES = ("pass", "fail", "refused", "error", "not_offered")


def load_pairs(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["pairs"]


def _with_reference_units(pair):
    """Copy of the pair plus the unit each output must be reported in."""
    copy = dict(pair)
    copy["reference_units"] = {
        out["name"]: out["unit"] for out in pair["reference"].get("outputs", [])
    }
    return copy


def compare(reference_output, got):
    """Compare one number with its reference. Returns a dict for the report."""
    expected = to_fraction(reference_output["value"])
    tolerance = to_fraction(reference_output["tolerance"]["value"])
    if not isinstance(got, (int, float)) or isinstance(got, bool) or not math.isfinite(got):
        return {"got": repr(got), "within_tolerance": False, "difference": None}
    difference = abs(Fraction(got) - expected)
    if reference_output["tolerance"]["kind"] == "relative":
        if expected == 0:
            # A relative tolerance has no meaning at zero; only an exact zero passes.
            measure = None
            ok = difference == 0
        else:
            measure = difference / abs(expected)
            ok = measure <= tolerance
    else:
        measure = difference
        ok = difference <= tolerance
    return {
        "got": got,
        "within_tolerance": ok,
        "difference": None if measure is None else float(measure),
        "difference_kind": reference_output["tolerance"]["kind"],
    }


def run_pair(adapter, pair):
    """Run one pair. Returns {'status': ..., 'outputs': {...}, 'note': ...}."""
    must_refuse = pair["reference"].get("outcome") == "refuse"
    try:
        answers = adapter.solve(_with_reference_units(pair))
    except NotOffered as exc:
        return {"status": "not_offered", "note": str(exc)}
    except Refused as exc:
        return {"status": "pass" if must_refuse else "refused", "note": str(exc)}
    except Exception as exc:  # the tool itself failed; record it, do not hide it
        return {"status": "error", "note": "%s: %s" % (type(exc).__name__, exc)}
    if must_refuse:
        return {"status": "fail", "note": "returned %r for a task that must be refused" % (answers,)}
    outputs = {}
    ok = True
    for ref in pair["reference"]["outputs"]:
        if ref["name"] not in answers:
            outputs[ref["name"]] = {"got": None, "within_tolerance": False, "difference": None}
            ok = False
            continue
        value, unit = answers[ref["name"]]
        if unit != ref["unit"]:
            outputs[ref["name"]] = {"got": value, "within_tolerance": False, "difference": None,
                                    "note": "answer in %s, reference in %s" % (unit, ref["unit"])}
            ok = False
            continue
        outputs[ref["name"]] = compare(ref, value)
        outputs[ref["name"]]["expected"] = ref["value"]
        outputs[ref["name"]]["unit"] = ref["unit"]
        ok = ok and outputs[ref["name"]]["within_tolerance"]
    return {"status": "pass" if ok else "fail", "outputs": outputs}


def run_all(adapters, pairs):
    """Run every pair on every adapter. Returns a plain dict ready for JSON."""
    tools = []
    for adapter in adapters:
        results = {pair["id"]: run_pair(adapter, pair) for pair in pairs}
        tools.append({"name": adapter.name, "versions": adapter.versions(), "results": results})
    return {"pairs": [{"id": p["id"], "category": p["category"], "task": p["task"]} for p in pairs],
            "tools": tools}


def summarize(run):
    """Counts of each status per tool and category."""
    summary = {}
    category = {p["id"]: p["category"] for p in run["pairs"]}
    for tool in run["tools"]:
        table = {}
        for pid, result in tool["results"].items():
            row = table.setdefault(category[pid], dict.fromkeys(STATUSES, 0))
            row[result["status"]] += 1
        summary[tool["name"]] = table
    return summary
