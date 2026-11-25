"""Tests for the parts of tools/round.py that need no network.

Run: python3 -m unittest discover -s tests -v
Written by Claude (AI).
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)
import round as round_script  # noqa: E402
from bench.__main__ import ADAPTERS  # noqa: E402

BY_KEY = {tool["key"]: tool for tool in round_script.TOOLS}


class ToolsTable(unittest.TestCase):
    def test_every_adapter_is_in_the_round_or_waiting_for_the_next(self):
        waiting = round_script.WAITING_FOR_THE_NEXT_ROUND
        self.assertEqual(sorted(list(BY_KEY) + list(waiting)), sorted(ADAPTERS))
        self.assertFalse(set(BY_KEY) & set(waiting))

    def test_the_round_of_december_has_the_eight_announced_tools(self):
        self.assertEqual(len(BY_KEY), 8)

    def test_no_tool_is_pinned_to_a_version(self):
        for tool in round_script.TOOLS:
            for argument in tool.get("install", []):
                for sign in ("==", "<", ">", "~="):
                    self.assertNotIn(sign, argument, tool["key"])

    def test_a_server_has_a_command_and_a_library_has_imports(self):
        for tool in round_script.TOOLS:
            self.assertIn("command" if tool["kind"] == "server" else "imports", tool)


class PipArguments(unittest.TestCase):
    def test_index_tool(self):
        self.assertEqual(round_script.pip_arguments(BY_KEY["ucon-mcp"], {}), ["ucon-tools[mcp]"])

    def test_repository_tool_needs_a_named_commit(self):
        with self.assertRaises(SystemExit):
            round_script.pip_arguments(BY_KEY["mcp-units"], {})
        self.assertEqual(
            round_script.pip_arguments(BY_KEY["mcp-units"], {"mcp-units": "abc"}),
            ["mcp-units @ git+https://github.com/quantumleeps/mcp-units@abc"])

    def test_workaround_is_added_only_when_asked(self):
        tool = BY_KEY["measurement-uncertainty-mcp"]
        commits = {tool["key"]: "abc"}
        self.assertNotIn("mcp<2", round_script.pip_arguments(tool, commits))
        self.assertEqual(round_script.pip_arguments(tool, commits, workaround=True)[-1], "mcp<2")


class Lines(unittest.TestCase):
    RECORD = {"name": "x", "installed": True, "started": True,
              "versions": {"x": "1.0", "mcp": "2.3.0"}, "detail": ""}

    def test_started(self):
        self.assertEqual(round_script.line(self.RECORD),
                         "- **x**: installed, started. mcp 2.3.0, x 1.0")

    def test_did_not_start(self):
        record = dict(self.RECORD, started=False, detail="boom")
        self.assertEqual(round_script.line(record),
                         "- **x**: installed (mcp 2.3.0, x 1.0), did not start. boom")

    def test_did_not_install(self):
        record = dict(self.RECORD, installed=False, started=False, versions={}, detail="no")
        self.assertEqual(round_script.line(record), "- **x**: did not install. no")

    def test_workaround_is_in_the_label(self):
        record = dict(self.RECORD, workaround=["mcp<2"])
        self.assertIn("**x (with the workaround `mcp<2`)**", round_script.line(record))


if __name__ == "__main__":
    unittest.main()
