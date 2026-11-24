"""Put every reference pair to one tool and record what came back.

An adapter is an object with:

    name            a short label for the tool
    versions()      dict of package name -> version string
    solve(pair)     one of the answers below, for one pair

`solve` returns `Answer({"value": 25.4})` with one number per output name, in
the units the reference asks for; or `Refusal("why")` when the tool itself
refuses the calculation; or `Unsupported("why")` when the tool has no function
for this kind of task. Any exception that escapes `solve` is recorded as an
error. The adapter must not compute anything itself: if the tool cannot do the
task, the honest answer is `Unsupported`.

Verdicts:

    pass         every output is inside the tolerance, or a refusal was
                 expected and the tool refused
    fail         an output is outside the tolerance or missing, the tool
                 refused a valid task, or the tool answered a task it should
                 have refused
    unsupported  the tool has no function for this task; not a failure
    error        the adapter or the tool raised an unexpected exception

Written by Claude (AI).
"""
import json
import math
from fractions import Fraction

VERDICTS = ("pass", "fail", "unsupported", "error")


class Answer:
    def __init__(self, outputs):
        self.outputs = dict(outputs)


class Refusal:
    def __init__(self, message=""):
        self.message = str(message)


class Unsupported:
    def __init__(self, reason=""):
        self.reason = str(reason)


def load_pairs(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["pairs"]


def compare(output, got):
    """Compare one number from a tool with one reference output.

    Returns (ok, difference, relative_difference). The tool's number is taken
    exactly as the float it is; the reference and the tolerance are exact
    fractions, so the comparison itself adds no rounding.
    """
    if isinstance(got, bool) or not isinstance(got, (int, float)):
        raise TypeError("a tool answer must be a number, got %r" % (got,))
    if isinstance(got, float) and not math.isfinite(got):
        return False, got, None
    reference = Fraction(output["value"])
    tolerance = Fraction(output["tolerance"]["value"])
    difference = Fraction(got) - reference
    if output["tolerance"]["kind"] == "relative":
        allowed = tolerance * abs(reference)
    else:
        allowed = tolerance
    relative = float(difference / reference) if reference != 0 else None
    return abs(difference) <= allowed, float(difference), relative


def judge(pair, answer):
    """Turn an adapter's answer for one pair into a result record."""
    result = {"id": pair["id"], "category": pair["category"], "outputs": [], "note": ""}
    reference = pair["reference"]
    must_refuse = reference.get("outcome") == "refuse"

    if isinstance(answer, Unsupported):
        result["verdict"] = "unsupported"
        result["note"] = answer.reason
        return result
    if isinstance(answer, Refusal):
        result["verdict"] = "pass" if must_refuse else "fail"
        result["note"] = "refused: " + answer.message
        return result
    if not isinstance(answer, Answer):
        result["verdict"] = "error"
        result["note"] = "adapter returned %r" % (answer,)
        return result
    if must_refuse:
        result["verdict"] = "fail"
        result["note"] = "answered %r where a refusal was expected" % (answer.outputs,)
        return result

    verdict = "pass"
    for output in reference["outputs"]:
        record = {"name": output["name"], "unit": output["unit"], "reference": output["value"]}
        if output["name"] not in answer.outputs:
            record.update(got=None, ok=False)
            verdict = "fail"
        else:
            got = answer.outputs[output["name"]]
            try:
                ok, difference, relative = compare(output, got)
            except TypeError as exc:
                result["verdict"] = "error"
                result["note"] = str(exc)
                return result
            record.update(got=got, ok=ok, difference=difference, relative_difference=relative)
            if not ok:
                verdict = "fail"
        result["outputs"].append(record)
    result["verdict"] = verdict
    return result


def run(pairs, adapter):
    """Run all pairs through one adapter. Returns a report dict."""
    results = []
    for pair in pairs:
        try:
            answer = adapter.solve(pair)
        except Exception as exc:  # the report must survive a crashing tool
            results.append({"id": pair["id"], "category": pair["category"], "outputs": [],
                            "verdict": "error",
                            "note": "%s: %s" % (type(exc).__name__, exc)})
            continue
        results.append(judge(pair, answer))
    summary = {verdict: sum(1 for r in results if r["verdict"] == verdict)
               for verdict in VERDICTS}
    return {"tool": adapter.name, "versions": adapter.versions(),
            "summary": summary, "results": results}


def to_markdown(report):
    """A plain table of one report, for people."""
    versions = ", ".join("%s %s" % item for item in sorted(report["versions"].items()))
    lines = ["Tool: %s (%s)" % (report["tool"], versions), "",
             "| Pair | Verdict | Largest relative difference | Note |", "|---|---|---|---|"]
    for result in report["results"]:
        relatives = [abs(o["relative_difference"]) for o in result["outputs"]
                     if o.get("relative_difference") is not None]
        largest = "%.1e" % max(relatives) if relatives else ""
        note = result["note"].replace("|", "/")
        lines.append("| %s | %s | %s | %s |" % (result["id"], result["verdict"], largest, note))
    summary = report["summary"]
    lines += ["", "Summary: " + ", ".join("%d %s" % (summary[v], v) for v in VERDICTS)]
    return "\n".join(lines)
