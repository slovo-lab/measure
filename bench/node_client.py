"""Ask a JavaScript library one question through a small Node program.

`bench/adapters/node/ask.js` is started once per question with the request on
its standard input and answers with one JSON object. The libraries are
installed with `npm ci` in `bench/adapters/node` (versions in its
`package.json`), or anywhere else if NODE_PATH names the directory.

Written by Claude (AI).
"""
import json
import os
import shutil
import subprocess

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adapters", "node")
ASK = os.path.join(HERE, "ask.js")


class NodeError(RuntimeError):
    """Node or the library is missing, or the program did not answer."""


def ask(request, timeout=60):
    node = shutil.which("node")
    if not node:
        raise NodeError("node is not installed")
    done = subprocess.run([node, ASK], input=json.dumps(request), capture_output=True,
                          text=True, timeout=timeout, cwd=HERE)
    if done.returncode != 0 or not done.stdout:
        raise NodeError("no answer from node: %s" % done.stderr.strip()[:300])
    return json.loads(done.stdout)


def library_version(library):
    reply = ask({"library": library, "op": "version"})
    if not reply.get("ok"):
        raise NodeError(reply.get("error", "no version"))
    return {library: reply["version"], "node": reply["node"]}
