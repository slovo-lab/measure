# Who else tests tools for AI agents, and how Measure differs

*Русская версия: [2026-11-25-neighbours.ru.md](2026-11-25-neighbours.ru.md)*

Written by Claude (AI) on 25 November 2026, after the lab's owner asked to check the competitors. Three searches today, added to the prior-art search of 24 November ([`2026-11-24-new-checks-prior-art.md`](2026-11-24-new-checks-prior-art.md)). Pages were read as search excerpts. "Not found" means not found in these searches.

| Kind | Examples found | What they measure | A model in between? | Checks the number against a cited reference? |
|---|---|---|---|---|
| Benchmarks of agents that use tools | MCP-Bench, MCP-Atlas (36 servers, 1 000 tasks), MCP-AgentBench, MCP-Universe, MCPMark, MedMCP-Calc (medical calculators) | Whether a language model picks the right tool and reaches the right answer | Yes; that is the subject | No: the tool is assumed right |
| Scores of server quality | mcpscore (72 rules; says it never calls a tool), mcp-scorecard (10 checks, a score out of 100), a platform that scored 39 752 servers, graders of tool descriptions, agent-eval (12 servers, a model as judge) | Protocol, schemas, descriptions, security, install | Some | No |
| "Does it work" audits | MCP Verified (weekly), Digital Applied, The Ops Log | Installs, starts, lists tools | No | No |
| Test frameworks for authors | mcp-assert, mcp-test-harness | Whatever the author writes as a test | No | Only if the author supplies one |
| Accuracy with a model in the loop | mcp-data-check | Model and server together, 5% tolerance | Yes | Against a table the user supplies |
| The method Measure borrows, in another field | TraCIM (metrology software), NIST's statistical reference datasets | Numerical correctness against reference data | No | Yes, but not for tools given to agents |

**What was not found:** anyone who puts questions with cited reference answers straight to the calculators that agents call, across many tools, and publishes what each answered. That is the place Measure stands in.

**What follows, honestly:**

1. The neighbourhood is crowded and better known than this lab. A reader will ask "is this not MCP-Bench?" The first paragraph of every report should answer it: no model, a cited reference for every answer, tolerances down to 1e-12.
2. A score is what the neighbours sell. One server found today carries a badge of 86 out of 100 from such a scorecard, does not start after a fresh install, and converts a pound with six digits. A score of form says nothing about the number. Measure gives no score, and this is the reason to keep it so.
3. The two closest relatives in method are in metrology, not in AI tooling. That is who should read the first round's report.
