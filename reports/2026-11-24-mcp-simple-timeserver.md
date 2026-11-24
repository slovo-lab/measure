# Report for mcp-simple-timeserver: 24 hours reported across a clock change where 23 passed

Status: sent on 24 November 2026 from the owner's account, after he read the text: https://github.com/andybrandt/mcp-simple-timeserver/issues/12. Written by Claude (AI).
Where: https://github.com/andybrandt/mcp-simple-timeserver/issues (four issues there, none on this; checked 24 November 2026).

**Title:** `calculate_time_distance` reports 24 hours across a clock change where 23 hours pass

**Body:**

Hello. In mcp-simple-timeserver 3.3.2 the call

```
calculate_time_distance(from_date="2026-03-28T12:00:00", to_date="2026-03-29T12:00:00", unit="hours", timezone="Europe/Madrid")
```

answers

```
Distance: 24.00 hours
...
UTC Reference: From: 2026-03-28 11:00:00 UTC  To: 2026-03-29 10:00:00 UTC
```

The clocks in Madrid go forward that night, so 23 hours pass, as the two UTC moments in the same answer show. The distance seems to be taken from the two local times before they are converted to UTC (Python subtracts two datetimes that share a time zone by the clock face). Subtracting the UTC moments would give 23.

Dates without a clock change in between came out right in our test.

About this report: it was written by an AI (Claude), working for the open project slovo-lab, and is posted from the account of the project's owner, who read it first. The questions and results for six time servers are here: https://github.com/slovo-lab/measure/tree/main/pilots/time
