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

Format version 2 (see FORMAT.md) adds one verdict and two things an adapter
may report:

    incomplete   the number is right, and something the answer had to say is
                 missing: which of several readings was taken, or a label
                 such as the unit

    Answer(outputs, stated={...})   what the tool itself said besides the
                 number, word for word, by label ("unit", "reading", ...).
                 `stated=None`, the default, means the adapter does not report
                 this at all; such a question is then recorded as unsupported,
                 with a note that the gap is in the adapter, not in the tool.
                 `stated={}` means the tool said nothing.
    Answer(outputs, also=[{...}])   further sets of outputs, when the tool
                 gave more than one answer to one question.

Version 1 pairs are judged exactly as before, and a report on them has the
same four counts as before.

Written by Claude (AI).
"""
import ast
import json
import math
import operator
from fractions import Fraction

VERDICTS = ("pass", "fail", "unsupported", "error")
ALL_VERDICTS = ("pass", "incomplete", "fail", "unsupported", "error")


class Answer:
    def __init__(self, outputs, stated=None, also=None):
        self.outputs = dict(outputs)
        self.stated = None if stated is None else dict(stated)
        self.also = [dict(more) for more in (also or [])]


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


def question_view(item, task, inputs, outputs):
    """What an adapter is shown for a version 2 question: the task, the inputs
    and the names and units of the outputs wanted. No reference value is in it."""
    return {"id": item["id"], "category": item["category"], "task": task, "inputs": inputs,
            "reference": {"outputs": [{"name": o["name"], "unit": o["unit"]} for o in outputs]}}


def _said(stated, label):
    """The tool's own words for a label, trimmed and in lower case, or None."""
    value = stated.get(label)
    if value is None or value is False:
        return None
    return str(value).strip().lower()


def _matches(outputs, got):
    """True if `got` has every output of one reference answer inside its tolerance."""
    for output in outputs:
        if output["name"] not in got:
            return False
        try:
            ok, _difference, _relative = compare(output, got[output["name"]])
        except TypeError:
            return False
        if not ok:
            return False
    return True


def _judge_any_of(result, reference, answer):
    answers = reference["answers"]
    if isinstance(answer, Refusal):
        result["verdict"] = "pass" if reference["refusal_passes"] else "fail"
        result["note"] = "declined: " + answer.message
        return result
    given = [answer.outputs] + answer.also
    matched = set()
    for got in given:
        hits = [i for i, candidate in enumerate(answers) if _matches(candidate["outputs"], got)]
        if not hits:
            result["verdict"] = "fail"
            result["note"] = "gave %r, which is none of the %d right answers" % (got, len(answers))
            return result
        matched.update(hits)
    result["matched"] = sorted(answers[i]["reading"] for i in matched)
    if len(matched) == len(answers):
        result["verdict"] = "pass"
        result["note"] = "gave every right answer"
        return result
    if answer.stated is None:
        result["verdict"] = "unsupported"
        result["note"] = ("the adapter does not report what the tool states, so it cannot be "
                          "told whether the tool said which reading it took (a gap in the "
                          "adapter, not in the tool)")
        return result
    said = _said(answer.stated, "reading")
    index = next(iter(matched))
    if said is None:
        result["verdict"] = "incomplete"
        result["note"] = "gave the answer for %r and did not say which reading it took" % (
            answers[index]["reading"],)
        return result
    result["stated"] = {"reading": answer.stated["reading"]}
    names = {i: [w.lower() for w in candidate["stated_as"]] for i, candidate in enumerate(answers)}
    if any(word in said for word in names[index]):
        result["verdict"] = "pass"
        result["note"] = "gave the answer for %r and said so" % (answers[index]["reading"],)
    elif any(word in said for i, words in names.items() if i != index for word in words):
        result["verdict"] = "fail"
        result["note"] = "gave the answer for %r but named another reading: %r" % (
            answers[index]["reading"], answer.stated["reading"])
    else:
        result["verdict"] = "incomplete"
        result["note"] = "gave the answer for %r; what it said, %r, does not tell which" % (
            answers[index]["reading"], answer.stated["reading"])
    return result


def _apply_must_state(result, must_state, answer):
    """After the numbers passed: check the labels the answer had to carry."""
    if answer.stated is None:
        result["verdict"] = "unsupported"
        result["note"] = ("the adapter does not report what the tool states (a gap in the "
                          "adapter, not in the tool)")
        return result
    result["stated"] = {}
    missing, wrong = [], []
    for item in must_state:
        label = item["what"]
        said = _said(answer.stated, label)
        if said is None:
            missing.append(label)
            continue
        result["stated"][label] = answer.stated[label]
        accept = item.get("accept")
        if accept is not None and said not in [word.lower() for word in accept]:
            wrong.append("%s stated as %r" % (label, answer.stated[label]))
    if wrong:
        result["verdict"] = "fail"
        result["note"] = "; ".join(wrong)
    elif missing:
        result["verdict"] = "incomplete"
        result["note"] = "did not state: " + ", ".join(missing)
    return result


def judge(pair, answer):
    """Turn an adapter's answer for one pair into a result record."""
    result = {"id": pair["id"], "category": pair["category"], "outputs": [], "note": ""}
    reference = pair["reference"]
    must_refuse = reference.get("outcome") == "refuse"

    if isinstance(answer, Unsupported):
        result["verdict"] = "unsupported"
        result["note"] = answer.reason
        return result
    if reference.get("outcome") == "any_of":
        if not isinstance(answer, (Answer, Refusal)):
            result["verdict"] = "error"
            result["note"] = "adapter returned %r" % (answer,)
            return result
        return _judge_any_of(result, reference, answer)
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
    if verdict == "pass" and reference.get("must_state"):
        return _apply_must_state(result, reference["must_state"], answer)
    return result


# ---- relations (format version 2) ------------------------------------------

_OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv, ast.Pow: operator.pow}


def _evaluate(expression, values):
    """Exact arithmetic over `call.output` names and plain numbers."""
    def walk(node):
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            operand = walk(node.operand)
            return -operand if isinstance(node.op, ast.USub) else operand
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            return values[(node.value.id, node.attr)]
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Fraction(repr(node.value))
        raise ValueError("not allowed in an expression: %s" % type(node).__name__)
    return walk(ast.parse(expression, mode="eval").body)


def _fill(value, values):
    """Replace {"from": "a.value"} by the tool's own earlier output, as a number
    string that reads back to exactly the float the tool returned."""
    if isinstance(value, dict) and set(value) == {"from"}:
        call, output = value["from"].split(".")
        return repr(float(values[(call, output)]))
    if isinstance(value, dict):
        return {key: _fill(inner, values) for key, inner in value.items()}
    if isinstance(value, list):
        return [_fill(inner, values) for inner in value]
    return value


def run_relation(item, adapter):
    """Make the calls of one relation, one feeding the next, and judge it."""
    result = {"id": item["id"], "category": item["category"], "kind": "relation",
              "outputs": [], "note": "", "calls": {}}
    values = {}
    for call in item["calls"]:
        inputs = _fill(call["inputs"], values)
        answer = adapter.solve(question_view(
            {"id": "%s/%s" % (item["id"], call["name"]), "category": item["category"]},
            call["task"], inputs, call["outputs"]))
        if isinstance(answer, Unsupported):
            result["verdict"] = "unsupported"
            result["note"] = "call %r: %s" % (call["name"], answer.reason)
            return result
        if isinstance(answer, Refusal):
            result["verdict"] = "fail"
            result["note"] = "call %r was refused: %s" % (call["name"], answer.message)
            return result
        if not isinstance(answer, Answer):
            result["verdict"] = "error"
            result["note"] = "call %r: adapter returned %r" % (call["name"], answer)
            return result
        result["calls"][call["name"]] = dict(answer.outputs)
        for output in call["outputs"]:
            got = answer.outputs.get(output["name"])
            if (isinstance(got, bool) or not isinstance(got, (int, float))
                    or (isinstance(got, float) and not math.isfinite(got))):
                result["verdict"] = "fail"
                result["note"] = "call %r gave no usable number for %r: %r" % (
                    call["name"], output["name"], got)
                return result
            values[(call["name"], output["name"])] = Fraction(got)
    relation = item["relation"]
    left = _evaluate(relation["left"], values)
    right = _evaluate(relation["right"], values)
    tolerance = Fraction(relation["tolerance"]["value"])
    allowed = tolerance * max(abs(left), abs(right)) \
        if relation["tolerance"]["kind"] == "relative" else tolerance
    difference = left - right
    result.update(left=float(left), right=float(right), difference=float(difference))
    result["verdict"] = "pass" if abs(difference) <= allowed else "fail"
    if result["verdict"] == "fail":
        result["note"] = "%s = %r but %s = %r" % (relation["left"], float(left),
                                                   relation["right"], float(right))
    return result


def run(pairs, adapter):
    """Run all pairs through one adapter. Returns a report dict."""
    results = []
    for pair in pairs:
        try:
            if pair.get("kind") == "relation":
                results.append(run_relation(pair, adapter))
                continue
            if pair["reference"].get("outcome") == "any_of":
                # The adapter is shown the question only, never the answers.
                shown = question_view(pair, pair["task"], pair["inputs"],
                                      pair["reference"]["answers"][0]["outputs"])
            else:
                shown = pair
            answer = adapter.solve(shown)
        except Exception as exc:  # the report must survive a crashing tool
            results.append({"id": pair["id"], "category": pair["category"], "outputs": [],
                            "verdict": "error",
                            "note": "%s: %s" % (type(exc).__name__, exc)})
            continue
        results.append(judge(pair, answer))
    summary = {verdict: sum(1 for r in results if r["verdict"] == verdict)
               for verdict in VERDICTS}
    incomplete = sum(1 for r in results if r["verdict"] == "incomplete")
    if incomplete:      # only version 2 questions can earn it
        summary["incomplete"] = incomplete
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
    lines += ["", "Summary: " + ", ".join("%d %s" % (summary[v], v)
                                          for v in ALL_VERDICTS if v in summary)]
    return "\n".join(lines)
