# New kinds of check: what exists already

*Русская версия: [2026-11-24-new-checks-prior-art.ru.md](2026-11-24-new-checks-prior-art.ru.md)*

Written by Claude (AI) on 24 November 2026, evening. The owner agreed that day to four new kinds of check and to a kit for authors. The manifesto's rule 5 says to search before building. This file records the search: seven queries and eight pages read through a fetch tool that returns the page's content as a summary. Nothing here was installed or run. "Not found" means not found in these searches.

## Summary

| Idea | Does it exist? | What Measure does |
|---|---|---|
| A kit so that authors can run reference questions against their own server | Yes, as frameworks: `mcp-assert`, `mcp-test-harness`. Neither was found to ship reference questions for a field | Do not write a kit. Publish Measure's pairs so that such a framework can read them; decide which after reading their test formats |
| `mcp-data-check` as the runner | It answers a different question | Do not use it; name it as a neighbour |
| 2. Does the tool start after a fresh install | Yes, at the scale of the whole registry | Do not build an audit. Keep one "installed and started" line per tested tool in each monthly round, and point to the big audits |
| 1. Questions with no answer or with two | Found for language models, not for the tools they call | Build it; this is the gap |
| 3. Does the tool agree with itself | The method is old and has a name, metamorphic testing. Not found applied across calculators for agents | Build it, under that name, citing the method |
| 4. Does the answer say what it is | One 2026 study on the same failure in general; no check for calculators found | Build it, small, citing that study |

## The kit for authors

**mcp-assert** ([package index](https://pypi.org/project/mcp-assert/), MIT, repository `blackwell-systems/mcp-assert`). Describes itself as deterministic correctness testing for servers for AI agents, with no language model in between: one program that connects to a server, calls its tools and checks the results. Version 0.10.0 is dated 5 May 2026 and the index lists 0.12.3 from 4 June 2026. Not read: its documentation (the address redirected to another site and the fetch tool did not follow), so its test file format and its kinds of assertion are unknown to us. Read before deciding anything.

**mcp-test-harness** ([repository](https://github.com/vaquarkhan/mcp-test-harness), MIT, release 5.2.0). A test framework in the style of pytest that calls the protocol directly, with no language model. Its page describes checks of schema, snapshots, response time, repeated calls giving the same result, and expected errors; reports in several formats; an action for automatic runs; and a command that starts a server and does the handshake. Its page describes no numeric tolerance. It links a separate repository of test suites, which was not read.

**What follows.** A kit of our own would be a duplicate of the framework part. What neither page offers is the thing Measure has: questions for a field, each with a cited source. So the useful step is smaller than a kit: give the pairs in a form one of these frameworks can run, and tell authors which command to use. Before that: read `mcp-assert`'s documentation and the linked suites repository. Two things to look for: whether a number can be compared within a tolerance (ours go down to 1e-12), and whether "the tool must refuse" can be written.

## mcp-data-check

[Package index](https://pypi.org/project/mcp-data-check/), MIT, repository `GSA-TTS/mcp-data-check`, version 0.6.1 of 29 April 2026. It takes a table of questions and expected answers and reports how often a server leads to the right answer.

It is not a runner for Measure, for three reasons taken from its own page. A language model sits between the question and the server, so the result measures the model and the server together; Measure calls the tool directly so that the tool alone is tested. It needs a paid key for the model; the lab has none. A numeric answer passes within 5%; Measure's tolerances are between 1e-12 and 1e-4. A 5% tolerance would pass an area that is 0.2% too large, which is one of the findings the lab reported on 24 November.

It answers a real question that Measure does not: does an agent with this server do better than without it. It can run each question with and without the server and report the difference. Named here as a neighbour. Not used.

## 2. Does it start?

Three audits were read.

- **MCP Verified**, first report dated 19 October 2026 ([page](https://buttondown.com/mcpverified/archive/mcp-verified-1-427-of-750-mcp-servers-actually/)): 750 servers from public registries were installed, started with no credentials, asked for their list of tools, and given one call where a tool takes no arguments. 427 worked; of 150 from the Python package index, 73. Causes named: a missing key or configuration, a crash at start, a failed install, a dead address. The list is public; the data feed is paid; no code was linked.
- **Digital Applied**, 5 November 2026 ([page](https://www.digitalapplied.com/blog/mcp-server-reliability-100-server-stress-test-study)): 1 000 remote addresses sampled from the registry, handshake and list of tools only, repeated after 46 minutes; 550 completed the handshake and 338 asked for sign-in. Data and script are published, and the authors say they will repeat it about once a quarter.
- **The Ops Log**, July 2026, corrected in August ([page](https://dev.to/theopslog/i-checked-every-mcp-server-in-the-official-registry-about-1-in-10-is-broken-1ehj)): one handshake request to 10 716 remote addresses; the author published two corrections to the headline figure.

So the general question "what share of servers start" is taken, and by people with more reach than this lab. Measure will not build an audit.

What stays is narrower and is already agreed as part of a monthly round: every tool in the round is installed fresh on the day, and the report has one line per tool saying whether it installed and started, with the exact versions that were resolved and, if it did not start, the error. That is a condition of the measurement, as a calibration certificate states the conditions. The lab's five failures on 24 November all had one cause (a dependency declared with no upper bound resolving to a new major version). Whether the big audits name that cause is not known: the summaries read did not say.

## 1. Questions with no answer or with two

Search results were about language models: benchmarks of whether a model notices that a task is underspecified or cannot be answered. Nothing found puts such questions to the tools. The lab's three trials each met the case in a tool: a rate of return with two solutions answered with one and no note; a local time that occurs twice answered 05:30 by two servers and 06:30 by two; a time that does not exist answered by all.

This is the gap, and the next thing to build. The format already has one half of it: a pair whose reference is "refuse". The other half is new: a reference that says "there are two answers, these", and a rule for what passes.

## 3. Does the tool agree with itself?

This is metamorphic testing: when the right answer is unknown, test a relation that must hold between answers (there and back; the same quantity asked in two ways). The method dates from 1998; the usual reference is T. Y. Chen, S. C. Cheung and S. M. Yiu, "Metamorphic Testing: A New Approach for Generating Next Test Cases" (available as [arXiv:2002.12543](https://arxiv.org/abs/2002.12543); seen in search results, not read). `mcp-test-harness` has one relation of this kind built in: the same call twice gives the same result. No cross-tool use of such relations on calculators for agents was found.

Measure should use the established name and cite the method. Such a check needs no reference value, so the rule "every answer has a source" becomes "every relation has a source": the source must say why the relation holds.

## 4. Does the answer say what it is?

Two neighbours. A workshop paper at NeurIPS 2026, W. Jeffries, "Who Verifies the Tools? How Warped Formatters Mislead Agents and Their Verifiers" ([abstract](https://neurips.cc/virtual/2026/172953), abstract only read): the code that formats a tool's output drops facts the agent needs, though the tool is right, and agents then state things with no support. And a study of tool descriptions (Hasan and others, [arXiv:2602.14878](https://arxiv.org/abs/2602.14878)): 856 tools from 103 servers, almost all with at least one defect in the description. That one is about the text that describes a tool, not about its answers.

Neither is a check of whether a calculator's answer carries its unit, time zone or method. The first gives the idea outside support and should be cited. This kind of check is the least mechanical of the four (who decides that a label is sufficient?), so it starts small: for each pair, a list of words or fields the answer must contain, fixed in advance and published with the pair.

## What this changes in the plan

1. No kit and no audit. Two things dropped before they were started.
2. The `FORMAT.md` change covers kinds 1, 3 and 4. Kind 2 is not a pair; it belongs in the rules of a round (`ROUNDS.md`).
3. Before publishing pairs for other frameworks: read `mcp-assert`'s documentation and the suites repository linked from `mcp-test-harness`.

**Note of 27 November 2026.** The two documents named above as not read were read: see [`2026-11-27-test-frameworks.md`](2026-11-27-test-frameworks.md). Neither framework compares a number within a tolerance in its declarative form; the repository linked from `mcp-test-harness` holds connectors for other languages, not test suites for a field. No export of the pairs.
