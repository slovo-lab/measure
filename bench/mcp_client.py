"""Call tools on a server for AI agents (Model Context Protocol) over stdio.

The server is started as a child process and spoken to exactly as an agent's
host program would: initialize, then `tools/call`. The adapter code stays
synchronous; the conversation with the server runs on its own thread.

Needs the `mcp` package. Written by Claude (AI).
"""
import asyncio
import json
import os
import queue
import shutil
import sys
import threading


class ServerError(RuntimeError):
    """The server could not be started or did not answer."""


def find_command(name):
    """Path of a server's command.

    Looked for, in order: the environment variable MEASURE_SERVER_<NAME>
    (upper case, hyphens as underscores), for a server installed in an
    environment of its own; next to this Python; on PATH.
    """
    override = os.environ.get("MEASURE_SERVER_" + name.upper().replace("-", "_"))
    if override:
        if not os.path.exists(override):
            raise ServerError("%s does not exist" % override)
        return override
    beside = os.path.join(os.path.dirname(sys.executable), name)
    if os.path.exists(beside):
        return beside
    found = shutil.which(name)
    if not found:
        raise ServerError("command %r is not installed" % name)
    return found


class StdioServer:
    """One running server. Use as: with StdioServer("ucon-mcp") as server: ..."""

    def __init__(self, command, args=(), timeout=60):
        self._command = find_command(command)
        self._args = list(args)
        self._timeout = timeout
        self._requests = queue.Queue()
        self._thread = None
        self.server_name = None
        self.server_version = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.close()

    def start(self):
        if self._thread is not None:
            return
        ready = queue.Queue()
        self._thread = threading.Thread(target=lambda: asyncio.run(self._serve(ready)),
                                        daemon=True)
        self._thread.start()
        try:
            outcome = ready.get(timeout=self._timeout)
        except queue.Empty:
            raise ServerError("server %s did not start in %d s" % (self._command, self._timeout))
        if isinstance(outcome, Exception):
            raise ServerError("server %s failed to start: %s" % (self._command, outcome))

    def close(self):
        if self._thread is not None:
            self._requests.put(None)
            self._thread.join(timeout=10)
            self._thread = None

    def call(self, tool, arguments):
        """Call one tool. Returns (is_error, structured_or_parsed, text)."""
        self.start()
        answer = queue.Queue()
        self._requests.put((tool, arguments, answer))
        try:
            outcome = answer.get(timeout=self._timeout)
        except queue.Empty:
            raise ServerError("no answer from %s to %s in %d s" % (self._command, tool, self._timeout))
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    async def _next_request(self):
        """Wait for the next request without tying up a worker thread.

        The wait is a short sleep in a loop, so the thread that talks to the
        server stays a plain daemon thread and never keeps the program alive.
        """
        while True:
            try:
                return self._requests.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.02)

    async def _serve(self, ready):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        params = StdioServerParameters(command=self._command, args=self._args)
        try:
            with open(os.devnull, "w") as quiet:
                async with stdio_client(params, errlog=quiet) as (reader, writer):
                    async with ClientSession(reader, writer) as session:
                        info = await session.initialize()
                        self.server_name = info.serverInfo.name
                        self.server_version = info.serverInfo.version
                        ready.put(True)
                        while True:
                            request = await self._next_request()
                            if request is None:
                                return
                            tool, arguments, answer = request
                            try:
                                result = await session.call_tool(tool, arguments)
                                text = "\n".join(c.text for c in result.content
                                                 if getattr(c, "text", None))
                                answer.put((bool(result.isError), _payload(result, text), text))
                            except Exception as exc:
                                answer.put(exc)
        except Exception as exc:
            ready.put(exc)


def _payload(result, text):
    """The tool's answer as a Python object, if it sent one."""
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        # Servers built with FastMCP wrap a plain return value as {"result": ...}.
        if set(structured) == {"result"} and isinstance(structured["result"], dict):
            return structured["result"]
        return structured
    try:
        return json.loads(text)
    except ValueError:
        return None
