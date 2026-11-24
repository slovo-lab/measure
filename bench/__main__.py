"""Command line: python3 -m bench [--pairs FILE] [--json] ADAPTER

Written by Claude (AI).
"""
import argparse
import json
import sys

from bench import runner

ADAPTERS = {
    "pint": ("bench.adapters.pint_uncertainties", "PintUncertaintiesAdapter"),
}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m bench",
                                     description="Put the reference pairs to one tool.")
    parser.add_argument("adapter", choices=sorted(ADAPTERS))
    parser.add_argument("--pairs", default="pairs/pairs.json")
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    args = parser.parse_args(argv)

    module_name, class_name = ADAPTERS[args.adapter]
    module = __import__(module_name, fromlist=[class_name])
    report = runner.run(runner.load_pairs(args.pairs), getattr(module, class_name)())
    print(json.dumps(report, indent=2) if args.json else runner.to_markdown(report))
    return 1 if report["summary"]["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
