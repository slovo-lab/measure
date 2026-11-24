# A trial: position questions for servers for AI agents

*Русская версия: [README.ru.md](README.ru.md)*

Written by Claude (AI) on 24 November 2026. A one-day trial, not part of the bench, run at the lab owner's request after the [time trial](../time/README.md). The question: **do geospatial servers for AI agents disagree with reference answers?**

## What was done

Sixteen questions, four servers, 36 answers. References:

- a published worked example: Flinders Peak to Buninyong, 54 972.271 m, and Flinders Peak on the Map Grid of Australia, E 273 741.297, N 5 796 489.777 (Geocentric Datum of Australia technical manual; the numbers were written from memory and then confirmed to the millimetre by two independent calculations, the manual itself was not re-read today);
- the closed formula for Web Mercator, computed with 40 digits;
- GeographicLib, C. Karney's reference implementation, for other distances and for areas on the ellipsoid.

Servers: gis-mcp-server 1.2.0, mcp-geo 0.3.0, mcp-server-proj 1.0.0, geospatial-mcp 0.1.0.

## What came out

Full table and the list of questions: [results-2026-11-24.md](results-2026-11-24.md). 20 answers agree, 11 differ, 5 are recorded behaviours.

**Point-to-point distances and coordinate conversions are right everywhere.** Barcelona to Madrid, the published Australian line, the near-antipodal case where the older method fails, across 180 degrees, over the pole; Web Mercator and the Australian grid to the millimetre.

**Lengths and areas are where it goes wrong.**

1. **mcp-geo doubles the length of a line.** Its `length` tool gives 1 012 600.29 m for the line Barcelona to Madrid; its own `distance` tool gives 506 300.15 m for the same two points. The length is exactly twice the distance: the tool measures the line there and back, as the perimeter of a closed figure.
2. **gis-mcp-server disagrees with itself.** Its `length` gives 506 439.26 m for that line and its `distance` gives 506 300.15 m: 139 m apart. The length is measured on a flat map projection, the distance on the ellipsoid.
3. **Areas are 0.11% to 0.20% too large** in gis-mcp-server and in geospatial-mcp, whose tool is called `calculate_accurate_metrics`: 12 322.5 km2 for the one-degree cell at the equator, where the area on the ellipsoid is 12 308.8 km2. Both measure on a flat projection. mcp-geo, which measures on the ellipsoid, agrees with the reference on all three area questions.
4. **A place that does not exist.** For latitude 91, gis-mcp-server reports an error; mcp-geo returns `NaN` as an answer.
5. **The UTM zone of Bergen.** gis-mcp-server says zone 31. The grid makes an exception over south-west Norway, where zone 32 is widened, and Bergen is in zone 32. (Confirmed the same day against the description published by the Swedish mapping authority, Lantmäteriet, and other sources: between 56°N and 64°N zone 32 is widened to 9°.)

**Recorded only.** British National Grid to WGS 84: all three servers give the same answer and none says which method was used or how accurate it is; the methods in use differ by metres. All servers read a pair of numbers as longitude, latitude, although the formal definition of EPSG:4326 has latitude first; none says so in the answer.

**Starting at all.** mcp-geo 0.3.0 and mcp-server-proj 1.0.0 did not start after a fresh install (the same cause as before: the new major version of the `mcp` package); both were tested with `mcp<2`. A fifth server, gis-mcp, could not be installed in this workspace: one of its dependencies failed to build.

## What this means

This is the first of the three trials where ordinary questions fail: a line's length and a polygon's area are everyday requests, and two of three servers get the length wrong and two of three get the area wrong by more than a tenth of a percent.

The cause is not the libraries, which are sound, but what the servers do around them: which routine they call and on which surface they measure.

Reports were sent to the authors on 24 November 2026, after the lab owner read them; texts and links are in `reports/`.
