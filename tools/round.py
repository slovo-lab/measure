#!/usr/bin/env python3
"""Run one round: fresh installs, one install-and-start line per tool, the questions.

Usage:
    python3 tools/round.py --out DIR --pairs-commit SHA \
        --commit mcp-units=SHA --commit measurement-uncertainty-mcp=SHA

What it does, in the order of ROUNDS.md, section 3:

1. Takes `pairs/pairs.json` as it stands at the named commit (`git show`), so
   that pairs added later are not asked.
2. Makes one empty environment per tool in DIR/envs and installs the tool
   there with pip, with no version given: the newest release that day. The two
   tools that are not on the package index are installed from their
   repositories at the commit named on the command line. The script refuses
   to guess that commit: a person or a session has to read the changes first.
3. Checks that the tool starts: a library is imported; a server is started and
   asked to initialize, the way an agent's host program does it.
4. If a tool does not install or does not start and a workaround is written in
   TOOLS below, makes a second environment with the workaround. Its lines and
   results carry the workaround in their label and are never merged with the
   first.
5. Puts the pairs to every tool that started, through the ordinary runner.

The client that talks to the servers is part of the bench, not a tool under
test. It lives in an environment of its own with a fixed version of the `mcp`
package (CLIENT_MCP), so that every server is spoken to by the same client.

Writes DIR/pairs.json, DIR/install.json, DIR/install.md and DIR/results.json.
It writes no report: that is written by hand from these files.

Written by Claude (AI).
"""
import argparse
import datetime
import json
import os
import platform
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

CLIENT_MCP = "mcp==1.30.0"

# key: the name used by `python3 -m bench`. install: what pip is given.
# repo: installed from this repository at a commit named on the command line.
# kind: "library" (imported; the runner runs inside the tool's environment) or
# "server" (started by its command; the runner runs in the client's environment).
# show: packages whose resolved versions go into the line.
# workaround: extra pip arguments for a second, labelled environment.
# Adapters that exist but are not in the announced round. The tools of a round
# are fixed by its announcement; an adapter written afterwards waits here and
# joins the next announcement.
WAITING_FOR_THE_NEXT_ROUND = ("metrolopy", "quantities", "mathjs", "js-quantities",
                               "p6plab-mcp-calculator")

TOOLS = [
    {"key": "pint", "name": "Pint + uncertainties", "kind": "library",
     "install": ["pint", "uncertainties", "numpy"], "imports": ["pint", "uncertainties"],
     "show": ["pint", "uncertainties", "numpy"]},
    {"key": "ucon", "name": "ucon", "kind": "library",
     "install": ["ucon"], "imports": ["ucon"], "show": ["ucon"]},
    {"key": "gtc", "name": "GTC", "kind": "library",
     "install": ["GTC"], "imports": ["GTC"], "show": ["GTC", "scipy", "numpy"]},
    {"key": "ucon-mcp", "name": "ucon-mcp", "kind": "server",
     "install": ["ucon-tools[mcp]"], "command": "ucon-mcp",
     "show": ["ucon-tools", "ucon", "mcp"]},
    {"key": "unit-converter-mcp", "name": "unit-converter-mcp", "kind": "server",
     "install": ["unit-converter-mcp"], "command": "unit-converter-mcp",
     "show": ["unit-converter-mcp", "mcp"]},
    {"key": "mcp-units", "name": "mcp-units", "kind": "server",
     "repo": "https://github.com/quantumleeps/mcp-units", "command": "mcp-units",
     "show": ["mcp-units", "pint", "mcp"]},
    {"key": "mcp-gnu-units", "name": "mcp-gnu-units", "kind": "server",
     "install": ["mcp-gnu-units"], "command": "mcp-gnu-units",
     "show": ["mcp-gnu-units", "mcp"]},
    {"key": "measurement-uncertainty-mcp", "name": "measurement-uncertainty-mcp",
     "kind": "server", "repo": "https://github.com/kyb8801/measurement-uncertainty-mcp",
     "command": "measurement-uncertainty-mcp",
     "show": ["measurement-uncertainty-mcp", "mcp", "numpy", "scipy"],
     # Known since 24 November 2026: the server does not start with mcp 2.x.
     "workaround": ["mcp<2"]},
]


def pip_arguments(tool, commits, workaround=False):
    """What pip is asked to install for one tool."""
    if "repo" in tool:
        if tool["key"] not in commits:
            raise SystemExit("%s is installed from its repository: read the changes since "
                             "the last round, then name the commit with --commit %s=SHA"
                             % (tool["key"], tool["key"]))
        arguments = ["%s @ git+%s@%s" % (tool["key"], tool["repo"], commits[tool["key"]])]
    else:
        arguments = list(tool["install"])
    if workaround:
        arguments += tool["workaround"]
    return arguments


def line(record):
    """The install-and-start line of one tool, for the report."""
    label = record["name"]
    if record.get("workaround"):
        label += " (with the workaround `%s`)" % " ".join(record["workaround"])
    if not record["installed"]:
        return "- **%s**: did not install. %s" % (label, record["detail"])
    versions = ", ".join("%s %s" % item for item in sorted(record["versions"].items()))
    if not record["started"]:
        return "- **%s**: installed (%s), did not start. %s" % (label, versions, record["detail"])
    return "- **%s**: installed, started. %s" % (label, versions)


def _run(command, env=None, timeout=1200):
    done = subprocess.run(command, capture_output=True, text=True, env=env, timeout=timeout)
    return done.returncode, done.stdout, done.stderr


def _last(text, count=3):
    return " / ".join(l.strip() for l in text.strip().splitlines()[-count:] if l.strip())[:400]


def _python(env_dir):
    return os.path.join(env_dir, "bin", "python")


def make_env(env_dir, arguments):
    """An empty environment with `arguments` installed. Returns (ok, detail)."""
    code, _, err = _run([sys.executable, "-m", "venv", env_dir])
    if code:
        return False, _last(err)
    code, out, err = _run([_python(env_dir), "-m", "pip", "install", "--no-input"] + arguments)
    return code == 0, "" if code == 0 else _last(err or out)


def versions_in(env_dir, names):
    code, out, _ = _run([_python(env_dir), "-m", "pip", "list", "--format=json"])
    have = {p["name"].lower().replace("_", "-"): p["version"] for p in json.loads(out)} if not code else {}
    return {name: have[name.lower()] for name in names if name.lower() in have}


def _child_env(tool, env_dir):
    env = dict(os.environ)
    if tool["kind"] == "server":
        variable = "MEASURE_SERVER_" + tool["command"].upper().replace("-", "_")
        env[variable] = os.path.join(env_dir, "bin", tool["command"])
    return env


def check_start(tool, env_dir, client_dir):
    """Does the tool start? Returns (ok, detail)."""
    if tool["kind"] == "library":
        code, out, err = _run([_python(env_dir), "-c", "import " + ", ".join(tool["imports"])])
    else:
        if not os.path.exists(os.path.join(env_dir, "bin", tool["command"])):
            return False, "the command `%s` was not installed" % tool["command"]
        command = os.path.join(env_dir, "bin", tool["command"])
        code, out, err = _run([_python(client_dir), os.path.abspath(__file__),
                               "_start", tool["command"]], env=_child_env(tool, env_dir))
        if code:
            return False, "The server's own last words: `%s`" % server_last_words(command)
    return code == 0, "" if code == 0 else _last(err or out)


def server_last_words(command):
    """The last line a server writes when started with nothing to read."""
    try:
        done = subprocess.run([command], stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "(none in 30 s)"
    return _last(done.stderr or done.stdout, 1) or "(none)"


def ask(tool, env_dir, client_dir, pairs_file, versions):
    """Put the pairs to one tool. Returns the runner's report, or an error text."""
    python = _python(env_dir if tool["kind"] == "library" else client_dir)
    env = _child_env(tool, env_dir)
    env["MEASURE_ROUND_VERSIONS"] = json.dumps(versions)
    code, out, err = _run([python, os.path.abspath(__file__), "_ask", tool["key"], pairs_file],
                          env=env)
    try:
        return json.loads(out)
    except ValueError:
        return "the runner gave no report (exit %d): %s" % (code, _last(err or out))


def _start(command):
    """Child process, in the client's environment: start a server, say who it is."""
    from bench.mcp_client import StdioServer
    with StdioServer(command) as server:
        print(json.dumps({"name": server.server_name, "version": server.server_version}))


def _ask(key, pairs_file):
    """Child process: run the pairs through one adapter, print the report."""
    from bench import runner
    from bench.__main__ import ADAPTERS
    module_name, class_name = ADAPTERS[key]
    adapter = getattr(__import__(module_name, fromlist=[class_name]), class_name)()
    resolved = json.loads(os.environ.get("MEASURE_ROUND_VERSIONS", "{}"))
    own = adapter.versions

    def versions():
        # For a server the runner sits in the client's environment, where the
        # server's packages are not installed; the versions come from the
        # server's own environment. What the server says about itself is kept.
        try:
            said = own()
        except Exception:
            said = {}
        return {**said, **resolved}

    adapter.versions = versions
    try:
        report = runner.run(runner.load_pairs(pairs_file), adapter)
    finally:
        if hasattr(adapter, "close"):
            adapter.close()
    print(json.dumps(report))


def one_tool(tool, args, commits, client_dir, pairs_file, workaround=False):
    env_dir = os.path.join(args.out, "envs", tool["key"] + ("+workaround" if workaround else ""))
    arguments = pip_arguments(tool, commits, workaround)
    record = {"key": tool["key"], "name": tool["name"], "pip": arguments,
              "installed": False, "started": False, "versions": {}, "detail": ""}
    if workaround:
        record["workaround"] = tool["workaround"]
    record["installed"], record["detail"] = make_env(env_dir, arguments)
    report = None
    if record["installed"]:
        record["versions"] = versions_in(env_dir, tool["show"])
        record["started"], record["detail"] = check_start(tool, env_dir, client_dir)
    if record["started"] and not args.no_questions:
        report = ask(tool, env_dir, client_dir, pairs_file, record["versions"])
        if isinstance(report, str):
            record["detail"], report = report, None
        else:
            report["key"] = tool["key"]
            if workaround:
                report["workaround"] = tool["workaround"]
    print(line(record), flush=True)
    return record, report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run one round of Measure.")
    parser.add_argument("--out", required=True, help="directory for environments and output")
    parser.add_argument("--pairs-commit", required=True,
                        help="the commit named in the announcement")
    parser.add_argument("--commit", action="append", default=[], metavar="TOOL=SHA",
                        help="commit for a tool installed from its repository")
    parser.add_argument("--only", help="comma-separated tool keys (for trying the script)")
    parser.add_argument("--no-questions", action="store_true",
                        help="install and start only")
    args = parser.parse_args(argv)
    commits = dict(item.split("=", 1) for item in args.commit)
    tools = [t for t in TOOLS if not args.only or t["key"] in args.only.split(",")]
    for tool in tools:
        pip_arguments(tool, commits)  # refuse now, not after ten minutes of installs

    os.makedirs(args.out, exist_ok=True)
    if os.path.exists(os.path.join(args.out, "envs")):
        raise SystemExit("%s/envs exists: a round starts from empty environments" % args.out)
    code, pairs_text, err = _run(["git", "-C", ROOT, "show",
                                  args.pairs_commit + ":pairs/pairs.json"])
    if code:
        raise SystemExit("cannot read the pairs at %s: %s" % (args.pairs_commit, _last(err)))
    pairs_file = os.path.join(args.out, "pairs.json")
    with open(pairs_file, "w") as handle:
        handle.write(pairs_text)

    client_dir = os.path.join(args.out, "envs", "_client")
    ok, detail = make_env(client_dir, [CLIENT_MCP])
    if not ok:
        raise SystemExit("the bench's own client could not be installed: " + detail)

    records, reports = [], []
    for tool in tools:
        record, report = one_tool(tool, args, commits, client_dir, pairs_file)
        records.append(record)
        if report:
            reports.append(report)
        if not record["started"] and "workaround" in tool:
            record, report = one_tool(tool, args, commits, client_dir, pairs_file, workaround=True)
            records.append(record)
            if report:
                reports.append(report)

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    header = {"run_at": stamp, "python": platform.python_version(),
              "pairs_commit": args.pairs_commit, "pairs": len(json.loads(pairs_text)["pairs"]),
              "client": CLIENT_MCP, "commits": commits}
    with open(os.path.join(args.out, "install.json"), "w") as handle:
        json.dump(dict(header, tools=records), handle, indent=2, sort_keys=True)
    with open(os.path.join(args.out, "install.md"), "w") as handle:
        handle.write("\n".join(line(r) for r in records) + "\n")
    with open(os.path.join(args.out, "results.json"), "w") as handle:
        json.dump(dict(header, reports=reports), handle, indent=2, sort_keys=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_start":
        _start(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "_ask":
        _ask(sys.argv[2], sys.argv[3])
    else:
        sys.exit(main())
