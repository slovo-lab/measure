# Outside issues: the watch list

*Русская версия: [issues.ru.md](issues.ru.md)*

Written by Claude (AI). Every report the lab has sent to the author of a tested tool, in one table, with the date each page was last read and what was there. All fourteen were opened on 24 November 2026 from the owner's account, each after he read the text. An answer from an author is one of the things counted on 19 January 2027 under the eight-week rule.

How to check, the cheap way (found 25 November): in a chat session, with the owner's computer on, his signed-in browser shows all of them with their state in one page, `https://github.com/issues/created`; single pages open there without the request limit. Scheduled sessions cannot do this. The older way: the session cannot read other people's issues through the API. Pages are read with web fetch, one at a time; github.com refuses several requests in a row, so a full pass may take two sessions. A page that was not read is marked "not read", never "no answer".

| Issue | About | Last read | State then |
|---|---|---|---|
| [ucon 395](https://github.com/withtwoemms/ucon/issues/395) | `nmi` read in two ways | 25 Nov 2026, 11:00 | open, no comments |
| [ucon 396](https://github.com/withtwoemms/ucon/issues/396) | uncertainty of `x * x` | 24 Nov 2026, 19:00 to 19:10 | no comments |
| [measurement-uncertainty-mcp 8](https://github.com/kyb8801/measurement-uncertainty-mcp/issues/8) | fresh install does not start | 24 Nov 2026, 19:00 to 19:10 | no comments |
| [measurement-uncertainty-mcp 9](https://github.com/kyb8801/measurement-uncertainty-mcp/issues/9) | offer of a propagation tool | 24 Nov 2026, 19:00 to 19:10 | no comments |
| [unit-converter-mcp 4](https://github.com/zazencodes/unit-converter-mcp/issues/4) | passed; how we call it | 24 Nov 2026, 19:00 to 19:10 | no comments |
| [mcp-units 1](https://github.com/quantumleeps/mcp-units/issues/1) | passed; how we call it | 24 Nov 2026, 19:00 to 19:10 | open, no comments |
| [mcp-gnu-units 2](https://github.com/laszlopere/mcp-gnu-units/issues/2) | passed; how we call it | 24 Nov 2026, 19:00 to 19:10 | **closed as completed by the author (laszlopere) on 24 Nov 2026, without a comment** |
| [personal-finance-mcp 17](https://github.com/sarveshtalele/personal-finance-mcp/issues/17) | fresh install does not start | 24 Nov 2026, 19:00 to 19:10 | no comments |
| [vibe-math-mcp 4](https://github.com/apetta/vibe-math-mcp/issues/4) | rate of return: NaN, and one of two rates | 24 Nov 2026, 19:00 to 19:10 | no comments |
| [mcp-simple-timeserver 12](https://github.com/andybrandt/mcp-simple-timeserver/issues/12) | time trial finding | 25 Nov 2026, 11:00 | open, no comments |
| [mcp-time 17](https://github.com/TheoBrigitte/mcp-time/issues/17) | time trial finding | 25 Nov 2026, 11:00 | open, no comments |
| [geo-mcp 13](https://github.com/tabibhasann/geo-mcp/issues/13) | coordinates trial finding | 25 Nov 2026, 11:00 | open, no comments |
| [GIS-MCP-Server 4](https://github.com/matbel91765/GIS-MCP-Server/issues/4) | coordinates trial finding | 25 Nov 2026, 11:00 | open, no comments |
| [mcp-server-proj 1](https://github.com/radial-hks/mcp-server-proj/issues/1) | fresh install does not start | 24 Nov 2026, 19:00 to 19:10 | no comments |

## Log

- **24 November 2026, evening.** First pass, a few hours after the issues were opened. Nine pages read, five refused by github.com's request limit after three tries (ucon 395, mcp-simple-timeserver 12, mcp-time 17, geo-mcp 13, GIS-MCP-Server 4). One reaction: the author of mcp-gnu-units closed our note as completed. That note reported a pass and said it could be closed once read, so this is the expected outcome; it is the first sign that an author outside the lab has read a Measure report. It is counted as "read by an author", not as "uses the results".
- **25 November 2026, 10:30.** No page read. The scheduled session ran with nobody present, and reading pages outside the lab needed a permission that was not answered; one request was made and, as told, not repeated. All fourteen stay as in the table: the dates in "Last read" are the last real readings.
- **25 November 2026, about 11:00.** Read from a chat session through the owner's browser. The list page showed fourteen issues: thirteen open, one closed (mcp-gnu-units 2), no comment counter on any. The five pages never read before were opened one by one: open, no comments, no other activity (on geo-mcp 13 the only event is the `bug` label that came with the repository's template). The other nine rows keep their dates of 24 November; the list page alone is not a reading of a page. Noticed: on two of the pages opened (mcp-simple-timeserver 12, GIS-MCP-Server 4) the owner's account is not subscribed to notifications, so an answer there would not reach him by email.

By e-mail, 25 November 2026: p6plab-mcp-calculator (rounding; placeholder `convert_units`), to the address in the package metadata, because its repository is not reachable. Text: [`reports/2026-11-25-p6plab-mcp-calculator.md`](../reports/2026-11-25-p6plab-mcp-calculator.md). No answer yet.

Opened on 25 November 2026 (sixteen outside issues in all, and one e-mail):

- astropy 20948, the gallon defined through a rounded factor: https://github.com/astropy/astropy/issues/20948. No answer yet.
- js-quantities 153, the gallon and the pint stored as rounded values: https://github.com/gentooboontoo/js-quantities/issues/153. No answer yet.
