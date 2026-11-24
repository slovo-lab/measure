# Draft report for gis-mcp-server: length and distance disagree; areas on a flat projection; UTM zone of Bergen

Status: draft, not sent. Sending needs the lab owner's confirmation. Written by Claude (AI).
Where: https://github.com/matbel91765/gis-mcp-server/issues (no issues there on 24 November 2026).

**Title:** `length` and `distance` disagree by 139 m on the same line; two related observations

**Body:**

Hello. Three observations on gis-mcp-server 1.2.0. Its `distance` and `transform_crs` tools agreed with our reference values on every question, including a near-antipodal pair and a published worked example.

1. **`length` and `distance`.** For Barcelona (41.3874, 2.1686) to Madrid (40.4168, -3.7038), `distance` gives 506300.15 m (the geodesic value) and `length` of the LineString through the same two points gives 506439.26 m. It looks as if `length` measures on a projected plane. An agent that uses both tools gets two different lengths for one line.

2. **`area`.** For the one-degree cell `[[0,0],[1,0],[1,1],[0,1],[0,0]]` the answer is 12322539175.58 m2; the area on the WGS 84 ellipsoid is 12308778361 m2 (GeographicLib), a difference of 0.11%. For a cell of the same size across 180 degrees the difference is 0.20%. If the planar method is intended, saying so in the result's metadata, as `distance` already does with `"method":"geodesic"`, would help.

3. **`utm_zone` for Bergen.** `utm_zone(lat=60.39, lon=5.32)` returns zone 31. Between 56 N and 64 N zone 32 is widened to start at 3 E, so Bergen is in zone 32 (32V). The Svalbard case we tried (78.2 N, 15.6 E, zone 33) came out right.

About this report: it was written by an AI (Claude), working for the open project slovo-lab, and is posted from the account of the project's owner, who read it first. The questions and results for four servers are here: https://github.com/slovo-lab/measure/tree/main/pilots/coordinates
