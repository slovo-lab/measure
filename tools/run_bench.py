#!/usr/bin/env python3
"""Run the reference pairs against the tools under test and write the results.

Usage: python3 tools/run_bench.py [--date YYYY-MM-DD]
Writes results/<date>.json and RESULTS.md. Needs the packages listed in
requirements-bench.txt. Written by Claude (AI).
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
from bench.adapters.pint_uncertainties import PintUncertainties  # noqa: E402
from bench.adapters.ucon_adapter import Ucon  # noqa: E402

CATEGORY_NAMES = {
    "unit-conversion": "Unit conversion",
    "dimensional-safety": "Dimensional safety",
    "combined": "Combined uncertainty",
    "type-a": "Type A evaluation",
    "type-b": "Type B evaluation",
    "degrees-of-freedom": "Degrees of freedom",
    "reporting": "Reporting",
}


def _cell(row):
    asked = row["pass"] + row["fail"] + row["refused"] + row["error"]
    if asked == 0:
        return "not offered (%d)" % row["not_offered"]
    text = "%d of %d pass" % (row["pass"], asked)
    if row["not_offered"]:
        text += ", %d not offered" % row["not_offered"]
    return text


def _fmt(number):
    return "n/a" if number is None else "%.3g" % number


def markdown(run, date):
    summary = runner.summarize(run)
    tools = [t["name"] for t in run["tools"]]
    categories = [c for c in CATEGORY_NAMES if any(p["category"] == c for p in run["pairs"])]
    lines = [
        "# Measure: results",
        "",
        "Run on %s with Python %s. Written by a program; see `tools/run_bench.py`."
        % (date, platform.python_version()),
        "",
        "Each tool was given the %d reference pairs in [`pairs/pairs.json`](pairs/pairs.json). "
        "A pair passes when every answer is within the tolerance stated in the pair. "
        "The tolerances only allow for ordinary double-precision arithmetic." % len(run["pairs"]),
        "",
        "## Versions tested",
        "",
    ]
    for tool in run["tools"]:
        versions = ", ".join("%s %s" % kv for kv in sorted(tool["versions"].items()))
        lines.append("- **%s**: %s" % (tool["name"], versions))
    lines += ["", "## Summary", "", "| Category | Pairs | " + " | ".join(tools) + " |",
              "|---|---|" + "---|" * len(tools)]
    for category in categories:
        count = sum(1 for p in run["pairs"] if p["category"] == category)
        cells = [_cell(summary[t][category]) for t in tools]
        lines.append("| %s | %d | %s |" % (CATEGORY_NAMES[category], count, " | ".join(cells)))
    lines += [
        "",
        "\"Not offered\" means the tool has no feature for that kind of task. "
        "It is not counted as a failure.",
        "",
        "## What this does and does not show",
        "",
        "- It shows how each tool answered these %d questions on this date, with these versions." % len(run["pairs"]),
        "- It does not rank the tools, and a pass here does not certify a tool for any use.",
        "- The tools were called through their Python interfaces. Servers that wrap them for AI agents were not tested.",
        "- Categories with no pairs yet: " + (", ".join(
            CATEGORY_NAMES[c] for c in CATEGORY_NAMES if c not in categories) or "none") + ".",
        "",
        "## Every answer that was not a pass",
        "",
    ]
    any_listed = False
    for tool in run["tools"]:
        for pair in run["pairs"]:
            result = tool["results"][pair["id"]]
            if result["status"] in ("pass", "not_offered"):
                continue
            any_listed = True
            lines.append("### %s: `%s` (%s)" % (tool["name"], pair["id"], result["status"]))
            lines.append("")
            if result.get("note"):
                lines.append(result["note"])
                lines.append("")
            for name, out in result.get("outputs", {}).items():
                if out.get("within_tolerance"):
                    continue
                lines.append("- `%s`: reference %s %s, tool gave %s; %s difference %s"
                             % (name, out.get("expected"), out.get("unit", ""), out.get("got"),
                                out.get("difference_kind", ""), _fmt(out.get("difference"))))
            lines.append("")
    if not any_listed:
        lines += ["None.", ""]
    notes_path = os.path.join(ROOT, "results", date + "-notes.md")
    if os.path.exists(notes_path):
        with open(notes_path, encoding="utf-8") as handle:
            lines += [handle.read().rstrip(), ""]
    lines += ["## All results", "", "| Pair | " + " | ".join(tools) + " |",
              "|---|" + "---|" * len(tools)]
    for pair in run["pairs"]:
        cells = [t["results"][pair["id"]]["status"].replace("_", " ") for t in run["tools"]]
        lines.append("| `%s` | %s |" % (pair["id"], " | ".join(cells)))
    lines += ["", "Full numbers for every answer are in [`results/%s.json`](results/%s.json)."
              % (date, date), ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.date.today().isoformat())
    args = parser.parse_args()
    pairs = runner.load_pairs(os.path.join(ROOT, "pairs", "pairs.json"))
    run = runner.run_all([PintUncertainties(), Ucon()], pairs)
    run["date"] = args.date
    run["python"] = platform.python_version()
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", args.date + ".json"), "w", encoding="utf-8") as handle:
        json.dump(run, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(ROOT, "RESULTS.md"), "w", encoding="utf-8") as handle:
        handle.write(markdown(run, args.date))
    for tool, table in runner.summarize(run).items():
        totals = {s: sum(row[s] for row in table.values()) for s in runner.STATUSES}
        print(tool, totals)
    return 0


if __name__ == "__main__":
    sys.exit(main())
