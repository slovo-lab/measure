# Can Measure's pairs run inside mcp-assert or mcp-test-harness?

*Русская версия: [2026-11-27-test-frameworks.ru.md](2026-11-27-test-frameworks.ru.md)*

Written by Claude (AI) on 27 November 2026, in the morning scheduled session. The prior-art note of 24 November ([`2026-11-24-new-checks-prior-art.md`](2026-11-24-new-checks-prior-art.md)) decided not to write a test kit of our own, because two frameworks for testing servers for AI agents already exist, and left one question open: could Measure's reference pairs be given in a form one of them can run, so that a server's author checks his own server with one command? Two things had to be found out first: can a number be compared within a tolerance, and can "the tool must refuse" be written. This note answers both.

## What was read

Read as source code and documentation in the repositories, cloned for reading only. Nothing from them was installed or run (see "What failed" below).

| Project | Licence | What was read | Commit read |
|---|---|---|---|
| `blackwell-systems/mcp-assert` (package index: `mcp-assert` 0.12.3, 4 June 2026, a Go program in a Python wrapper) | MIT | `docs/writing-assertions.md` (the YAML format and the table of assertion types), `docs/architecture.md` (the `Expect` structure and the order of checks), `internal/assertion/checker.go` (how `json_path` compares) | `e5b2c09`, 27 November 2026 |
| `vaquarkhan/mcp-test-harness` (release 5.3.1, 24 October 2026) | MIT | `README.md`, `src/mcp_test_harness/assertions.py` (`assert_tool_call`) | `692cf2e` |
| `vaquarkhan/mcp-test-suite`, the repository the harness links as its "suite repo" (release 4.0.0) | MIT | `README.md`, `docs/tutorials/yaml.md` (the `mcp-suite.yaml` format), `src/mcp_test_suite/declarative.py` | `b41d08a` (branch `init`) |

The second link turned out not to be what the note of 24 November expected. `mcp-test-suite` is not a collection of test suites for particular fields; it is the set of connectors (a shared YAML file, adapters for Node, Java, Go and .NET, a GitHub Action) that let the harness run from other languages. It ships no reference questions.

## The two questions

**1. A number within a tolerance: no, in either framework's declarative form.**

- mcp-assert: the checks on a result are `equals` (exact text, whitespace trimmed), `contains`, `not_contains`, `matches_regex`, `in_order`, and `json_path`. In `checker.go`, `json_path` prints both the expected and the actual value as text and compares the two strings. There is no tolerance and no numeric comparison other than the special field `net_delta`.
- mcp-test-suite: a case has an `expected` payload; the tutorial and the code compare it for equality.
- mcp-test-harness: `assert_tool_call(session, tool, arguments, expected)` serializes the response content and compares it with `expected` for equality.

Measure's tolerances are small (`1e-12` relative for exact answers, `1e-9` for rounded ones; [`FORMAT.md`](../FORMAT.md)) but they are not zero: they exist because tools compute in double precision, and a tool whose answer is off in the last binary digit has not failed. An exact comparison would fail such a tool. A regular expression can imitate a tolerance for one number written in one way, but not for any value written in any way, and it would hide the reference in a pattern nobody can read.

The harness can also run tests written in Python, where a test can use any comparison it likes. But a test written in Python for a particular server is what Measure's adapters already are.

**2. "Must refuse": yes, in both, but narrower than in Measure.**

- mcp-assert: `is_error: true` passes when the tool sets the protocol's `isError` flag.
- mcp-test-suite: `expect_error` accepts `true`, a substring of the message, or a code; its code says that a failure of the test's own machinery must not count as the expected error, which is the right care.

Measure decides whether an answer is a refusal in each adapter, from what the server actually returns. Most servers refuse through `isError`, so for them this would carry over. It would not carry over for a tool that declines in ordinary text, or for one that returns `isError` for a fault of its own: the framework cannot tell the two apart, and Measure's adapters do (see `bench/adapters/unit_converter_mcp.py`, where only two kinds of error message count as a refusal and anything else is reported as a server error).

## The larger obstacle: every server speaks its own language

Even with a tolerance, a pair cannot be written once and run against any server. The pair "convert 1 inch to millimetres" becomes, for unit-converter-mcp, a call of the tool `convert_length` with the arguments `value`, `from_unit: "inch"`, `to_unit: "millimeter"`, and the answer is read from the field `converted_value`. For each of the other servers the tool name, the argument names, the spelling of the units and the shape of the answer are different. That translation is exactly what Measure's adapters do. An export for these frameworks would be one file per server, generated from the adapter's tables, and it would duplicate the adapter in a weaker form.

## Decision

- **No export of the pairs for these frameworks now.** With exact comparison it would fail correct tools, and it would create a second set of verdicts next to Measure's own, which could disagree.
- **For a server's author who wants to check his own server, the route stays Measure itself:** an adapter (most are under 150 lines) and `python3 -m bench <tool>`. A short guide for authors on writing an adapter would serve them better than an export. Not started; it is not in the plan yet and is noted here as a candidate.
- **A possible contribution, not proposed to anyone:** a numeric comparison with a tolerance for `json_path` in mcp-assert would make the export worth doing. On 27 November its issue tracker had no issue mentioning "tolerance", "numeric", "float" or "approximate" (GitHub search; the harness's tracker had none for "tolerance", "numeric" or "approx" either). Writing to the authors would be posting outside the lab, which needs the owner's yes; it is not due now, because Measure does not need it.
- Both frameworks can repeat a call and compare the results (mcp-assert's `--trials`, the harness's repeated-call check). Measure's second run of every tool in a round (decided 25 November) is the same idea; nothing to take from them beyond naming them as neighbours.

## What failed

An attempt to install mcp-assert 0.12.3 and unit-converter-mcp 0.1.2 into a scratch environment, to try one pair through mcp-assert, was refused by the session's permission check. It was not retried or done another way. So nothing above was observed by running either framework; every statement comes from the source and documentation at the commits named in the table.
