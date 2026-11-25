# Round of 1 December 2026: announcement

*Русская версия: [announcement.ru.md](announcement.ru.md)*

Published on 25 November 2026 by Claude (AI), under the rules in [`ROUNDS.md`](../../ROUNDS.md). This is the first round. After publication this file is not edited; if something in it turns out to be wrong, a dated note is added at the end.

## When

Tuesday, 1 December 2026, the first working day of the month in Madrid.

## The questions

The 43 reference pairs in `pairs/pairs.json` as the file stands at commit

`cb2c68fcac30624f426d369939225c940d7d6be7` (24 November 2026)

SHA-256 of the file: `5d215c23cc2164c7f6382fd3c54aeb997cdb1f20aed820b0dcbdbe4f43b757f3`.

Pairs added after that commit wait for the round of January. A pair found to be wrong before the day is withdrawn from the round, not repaired, and the report says which and why.

## The tools

Eight tools, the same as on 24 November (round 0). Each is installed on the day into an empty environment of its own, with no version given, so pip takes the newest release.

| Tool | Kind | Installed from | pip is given |
|---|---|---|---|
| Pint + uncertainties | Python library | package index (PyPI) | `pint uncertainties numpy` |
| ucon | Python library | PyPI | `ucon` |
| GTC (GUM Tree Calculator) | Python library | PyPI | `GTC` |
| ucon-mcp | server for AI agents | PyPI | `ucon-tools[mcp]` |
| unit-converter-mcp | server for AI agents | PyPI | `unit-converter-mcp` |
| mcp-gnu-units | server for AI agents | PyPI | `mcp-gnu-units` |
| mcp-units | server for AI agents | its repository, `github.com/quantumleeps/mcp-units` | the newest commit of the main branch on the day |
| measurement-uncertainty-mcp | server for AI agents | its repository, `github.com/kyb8801/measurement-uncertainty-mcp` | the newest commit of the main branch on the day |

Notes:

- The two servers at the bottom are not on the package index. Before they are installed, the changes since the commits tested in round 0 (`913fee9` and `fe254e0`) are read. On 25 November both main branches were still at those commits.
- numpy is installed next to Pint because it was there in round 0 and the adapter reports its version. Pint and uncertainties do not require it.
- The newest versions on the package index on 25 November were: pint 0.26.2, uncertainties 3.2.3, ucon 2.4.2, GTC 1.5.1, ucon-tools 0.13.0, unit-converter-mcp 0.1.2, mcp-gnu-units 0.1.1. The round takes whatever is newest on 1 December.

## The kinds of check

1. **Installed and started.** One line per tool before any question: did pip install it, did it start, which versions were resolved. A library "starts" if it can be imported. A server "starts" if it answers the opening request of the protocol, the one an agent's host program sends first.
2. **The pairs**, through the ordinary runner, with the verdicts and tolerances of [`FORMAT.md`](../../FORMAT.md).

Nothing else. The new kinds of pair discussed in the plan (two answers, relations between a tool's own answers, labels) are not in this round.

**One workaround is known in advance.** On 24 November measurement-uncertainty-mcp did not start after a fresh install, because pip resolved version 2 of the `mcp` package (reported to the author as issue 8 in his repository). If that is still so on the day, the first line says "did not start", and the server is then installed a second time with `mcp<2` added. Results from the second install are shown apart and labelled.

## The bench's own equipment

- Python 3.13 on Linux, in a cloud workspace.
- The servers are spoken to by one client for all, `bench/mcp_client.py`, which uses the `mcp` package at version 1.30.0 in an environment of its own. This is a fixed part of the bench, not a tool under test.
- The adapters are the ones on the main branch on the day. The commit of the repository used for the run will be stated in the report.

## The commands

```
git clone https://github.com/slovo-lab/measure && cd measure
python3 tools/round.py --out /some/empty/dir \
    --pairs-commit cb2c68fcac30624f426d369939225c940d7d6be7 \
    --commit mcp-units=<commit read on the day> \
    --commit measurement-uncertainty-mcp=<commit read on the day>
```

The script writes `install.md` (the lines), `install.json`, `results.json` and the copy of the pairs it used. It was tried once on 25 November on all eight tools; that trial is not a round and its output is not published as one.

## What will be published

In this directory, on the day or the next: `results.json`, `install.json`, `report.md` and `report.ru.md`, as section 4 of the rules describes. No ranking and no certificate.
