# A trial: date and time questions for servers for AI agents

*Русская версия: [README.ru.md](README.ru.md)*

Written by Claude (AI) on 24 November 2026. A one-day trial, not part of the bench, run at the lab owner's request after the [money trial](../money/README.md). The question: **do time servers for AI agents disagree with reference answers?**

## What was done

Twenty-six questions, six servers, 76 answers. References come from the IANA time zone database (Python `zoneinfo`, tzdata 2026.6) and from calendar arithmetic in `trial.py`. None comes from a server.

Servers: mcp-server-time 2026.11.18, mcp-datetime 0.3.0, mcp-simple-timeserver 3.3.2 (Python); @theo.foobar/mcp-time 0.4.0, time-mcp 1.0.6, @brainycalc/mcptimeserver 1.0.8 (Node). All six started after a fresh install.

## What came out

Full table and the list of questions: [results-2026-11-24.md](results-2026-11-24.md). 61 answers agree with the reference, 1 differs, 14 are behaviours recorded where no single answer is right.

**The time zone database is handled correctly by everyone.** Offsets of 5 h 45 min and 10 h 30 min, Moscow in 2012, Samoa's skipped day in 2011, the rule changes of 2024 in Paraguay and Kazakhstan, the minute before and after the clocks change: every server that can answer gives the reference. So do leap years (1900, 2100), ISO week numbers and the Unix time just past the 32-bit limit.

**Three things are not right, or not safe.**

1. **Elapsed hours across a clock change.** From 12:00 on 28 March to 12:00 on 29 March 2026 in Madrid is 23 hours: the clocks go forward that night. mcp-simple-timeserver answers "24.00 hours", and in the same answer prints the two moments in UTC, 11:00 and 10:00, which are 23 hours apart. (Python itself does the same when two times in one zone are subtracted; the first version of this trial's reference made exactly that mistake and said 24.)
2. **A local time labelled as UTC.** Asked to convert `2026-01-15T12:00:00Z` to New York, @theo.foobar/mcp-time answers `2026-01-15T07:00:00Z`. The clock reading is right, but the `Z` at the end says "UTC", so the text names a moment five hours away from the right one. With `format: "RFC3339"` the same call gives `07:00:00-05:00`, which is right. The default output copies the shape of the input, including its `Z`.
3. **A time that occurs twice, and a time that does not exist.** 01:30 on 1 November 2026 happens twice in New York. Two servers return 05:30 UTC, two return 06:30 UTC, none says there was a choice. 02:30 on 8 March 2026 does not exist there. Three servers quietly answer as if it were 03:30 (07:30 UTC), one answers 06:30 UTC, none says the time was invalid. This is the same pattern as in the money trial: a question with two answers or none gets one confident answer.

**Conventions, recorded only.** 31 January plus one month gives 29 February in both servers that have the tool. The leap second 23:59:60 is refused by three servers and rolled into the next second by one.

**A limit, not an error.** The reference server mcp-server-time converts only a time of day on today's date, so it cannot be asked about any other date at all.

## What this means

The same as with money, and a little more. Ordinary questions pass everywhere, so a reference set of ordinary questions would be a table of passes. The edges are where tools differ, and here two of the edge findings are plain defects with a clear right answer (23 hours; a wrong `Z`).

Draft reports for the authors are in `reports/`; none is sent until the lab owner has read it.
