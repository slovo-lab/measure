#!/usr/bin/env python3
"""Run every adapter on the reference pairs and write the results.

Usage: python3 tools/make_results.py [--date YYYY-MM-DD]
Writes results/<date>.json and RESULTS.md. Needs the packages listed in
requirements-adapters.txt. If results/<date>-notes.md exists, its text is
included in RESULTS.md. Written by Claude (AI).
"""
import argparse
import datetime
import json
import os
import platform
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from bench import runner  # noqa: E402
from bench.__main__ import ADAPTERS  # noqa: E402

ORDER = ("pint", "ucon", "ucon-mcp", "unit-converter-mcp", "mcp-units", "mcp-gnu-units",
         "measurement-uncertainty-mcp")
CATEGORY_NAMES = {
    "unit-conversion": "Unit conversion",
    "dimensional-safety": "Dimensional safety",
    "combined": "Combined uncertainty",
    "type-a": "Type A evaluation",
    "type-b": "Type B evaluation",
    "degrees-of-freedom": "Degrees of freedom",
    "reporting": "Reporting",
}


def _adapter(key):
    module_name, class_name = ADAPTERS[key]
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)()


def _cell(results):
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in runner.VERDICTS}
    asked = counts["pass"] + counts["fail"] + counts["error"]
    if asked == 0:
        return "not offered (%d)" % counts["unsupported"]
    text = "%d of %d pass" % (counts["pass"], asked)
    if counts["unsupported"]:
        text += ", %d not offered" % counts["unsupported"]
    return text


def markdown(reports, pairs, date):
    names = [r["tool"] for r in reports]
    used = [c for c in CATEGORY_NAMES if any(p["category"] == c for p in pairs)]
    empty = [CATEGORY_NAMES[c] for c in CATEGORY_NAMES if c not in used]
    lines = [
        "# Measure: results",
        "",
        "Run on %s with Python %s. This file is written by `tools/make_results.py`; "
        "do not edit it by hand." % (date, platform.python_version()),
        "",
        "Each tool was given the %d reference pairs in [`pairs/pairs.json`](pairs/pairs.json). "
        "A pair passes when every answer is within the tolerance stated in the pair. "
        "Most tolerances only allow for ordinary double-precision arithmetic; "
        "the exceptions are explained in [`FORMAT.md`](FORMAT.md)." % len(pairs),
        "",
        "## Versions tested",
        "",
    ]
    for report in reports:
        versions = ", ".join("%s %s" % item for item in sorted(report["versions"].items()))
        lines.append("- **%s**: %s" % (report["tool"], versions))
    lines += ["", "## Summary", "", "| Category | Pairs | " + " | ".join(names) + " |",
              "|---|---|" + "---|" * len(names)]
    for category in used:
        count = sum(1 for p in pairs if p["category"] == category)
        cells = [_cell([r for r in report["results"] if r["category"] == category])
                 for report in reports]
        lines.append("| %s | %d | %s |" % (CATEGORY_NAMES[category], count, " | ".join(cells)))
    lines.append("| **All** | %d | %s |" % (
        len(pairs), " | ".join(_cell(report["results"]) for report in reports)))
    lines += [
        "",
        "\"Not offered\" means the tool has no function for that kind of task "
        "(the runner's verdict `unsupported`). It is not counted as a failure.",
        "",
        "## What this does and does not show",
        "",
        "- It shows how each tool answered these %d questions on this date, with these versions." % len(pairs),
        "- It does not rank the tools, and a pass here does not certify a tool for any use.",
        "- Tools marked \"(server)\" were started as servers for AI agents and called through their tools, the way an agent calls them. The others were called as Python libraries.",
        "- Categories with no pairs yet: %s." % (", ".join(empty) or "none"),
        "",
        "## Every answer that was not a pass",
        "",
    ]
    listed = False
    for report in reports:
        for result in report["results"]:
            if result["verdict"] in ("pass", "unsupported"):
                continue
            listed = True
            lines += ["### %s: `%s` (%s)" % (report["tool"], result["id"], result["verdict"]), ""]
            if result["note"]:
                lines += [result["note"], ""]
            for out in result["outputs"]:
                if out.get("ok"):
                    continue
                relative = out.get("relative_difference")
                lines.append("- `%s`: reference %s %s, tool gave %r%s" % (
                    out["name"], out["reference"], out["unit"], out.get("got"),
                    "" if relative is None else "; relative difference %.3g" % relative))
            lines.append("")
    if not listed:
        lines += ["None.", ""]
    notes_path = os.path.join(ROOT, "results", date + "-notes.md")
    if os.path.exists(notes_path):
        with open(notes_path, encoding="utf-8") as handle:
            lines += [handle.read().rstrip(), ""]
    lines += ["## All results", "", "| Pair | " + " | ".join(names) + " |",
              "|---|" + "---|" * len(names)]
    for index, pair in enumerate(pairs):
        cells = [report["results"][index]["verdict"].replace("unsupported", "not offered")
                 for report in reports]
        lines.append("| `%s` | %s |" % (pair["id"], " | ".join(cells)))
    lines += ["", "Every number behind this table is in [`results/%s.json`](results/%s.json)."
              % (date, date), ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.date.today().isoformat())
    args = parser.parse_args()
    pairs = runner.load_pairs(os.path.join(ROOT, "pairs", "pairs.json"))
    reports = []
    for key in ORDER:
        adapter = _adapter(key)
        try:
            reports.append(runner.run(pairs, adapter))
        finally:
            if hasattr(adapter, "close"):
                adapter.close()
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    record = {"date": args.date, "python": platform.python_version(),
              "pairs": len(pairs), "reports": reports}
    with open(os.path.join(ROOT, "results", args.date + ".json"), "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(ROOT, "RESULTS.md"), "w", encoding="utf-8") as handle:
        handle.write(markdown(reports, pairs, args.date))
    for report in reports:
        print(report["tool"], report["summary"])
    return 1 if any(r["summary"]["error"] for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
