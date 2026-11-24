# Draft report for personal-finance-mcp: does not start after a fresh install

Status: draft, not sent. Sending needs the lab owner's confirmation. Written by Claude (AI).
Where: https://github.com/sarveshtalele/personal-finance-mcp/issues (no existing issue on this, checked 24 November 2026).

**Title:** Server does not start after a fresh install (mcp 2.x removed `mcp.server.fastmcp`)

**Body:**

Hello. A fresh install of personal-finance-mcp 2.0.0 from PyPI on 24 November 2026 does not start:

```
python3 -m venv env && env/bin/pip install personal-finance-mcp==2.0.0
env/bin/personal-finance-mcp
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

The dependency is declared as `mcp[cli]>=1.0.0` (the same on `main` today), so pip now picks mcp 2.3.0, which no longer has that module. With `pip install "mcp<2"` in the same environment the server starts and works.

A possible fix is an upper bound, `mcp[cli]>=1.0.0,<2`, until the code is moved to the new interface.

About this report: it was written by an AI (Claude), working for the open project slovo-lab, and is posted from the account of the project's owner, who read it first. We found this while trying several finance servers with the same questions: https://github.com/slovo-lab/measure/tree/main/pilots/money
