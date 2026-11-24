# Draft report for mcp-server-proj: does not start after a fresh install

Status: draft, not sent. Sending needs the lab owner's confirmation. Written by Claude (AI).
Where: https://github.com/radial-hks/mcp-server-proj/issues (no issues there on 24 November 2026).

**Title:** Server does not start after a fresh install (mcp 2.x)

**Body:**

Hello. A fresh install of mcp-server-proj 1.0.0 from PyPI on 24 November 2026 does not start:

```
python3 -m venv env && env/bin/pip install mcp-server-proj==1.0.0
env/bin/mcp-server-proj
  File ".../mcp_server_proj/server.py", line 12, in <module>
    @server.list_tools()
AttributeError: 'Server' object has no attribute 'list_tools'
```

The dependency is declared as `mcp>=1.3.0`, so pip now picks mcp 2.3.0, where that interface changed. With `pip install "mcp<2"` in the same environment the server starts, and all three conversions we tried agreed with our reference values to the millimetre.

A possible fix is an upper bound, `mcp>=1.3.0,<2`, until the code is moved to the new interface.

About this report: it was written by an AI (Claude), working for the open project slovo-lab, and is posted from the account of the project's owner, who read it first. We found this while trying several geospatial servers with the same questions: https://github.com/slovo-lab/measure/tree/main/pilots/coordinates
