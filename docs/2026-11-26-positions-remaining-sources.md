# Positions: sources for the three questions that had none

*Русская версия: [2026-11-26-positions-remaining-sources.ru.md](2026-11-26-positions-remaining-sources.ru.md)*

Written by Claude (AI) on 26 November 2026, in the evening scheduled session. The note of 25 November ([`2026-11-25-positions-sources.md`](2026-11-25-positions-sources.md)) left three kinds of question out of the bench because no source had been read for them: the UTM zone exceptions over Norway and Svalbard, the area of a figure on the ellipsoid, and the length of a line given as a list of points. This note reads a source for each, or says why none is needed. Nothing here is in the round of 1 December; the earliest is 4 January 2027.

**How the sources were read.** As on 25 November: through a fetch tool that returns a document's text and answers questions about it. I did not see the typeset pages. The tool says which parts it gave verbatim and which only as a summary; only verbatim parts are used below. Every number was then recomputed by GeographicLib 2.1 and by PROJ 9.8.1 through pyproj 3.8.0. The script is [`pilots/coordinates/recompute_sources_2026_11_26.py`](../pilots/coordinates/recompute_sources_2026_11_26.py); its output is quoted below as it was run.

## 1. The UTM zone exceptions

**Source.** *Datums, Ellipsoids, Grids, and Grid Reference Systems*, DMA Technical Manual 8358.1, Defense Mapping Agency. https://apps.dtic.mil/sti/pdfs/ADA247651.pdf. The foreword says it is approved for public release with unlimited distribution. No edition date was found in the text that was read.

**What it says** (section 3-2, "The Grid Zone Designation", paragraph 3-2.2.1, read verbatim, described here in my own words): between latitudes 56° and 64° north, zone 32 is widened to 9° at the expense of zone 31, for southwest Norway. Between 72° and 84° north, zones 33 and 35 are widened to 12° for Svalbard, zones 31 and 37 are widened to 9°, and zones 32, 34 and 36 are not used. Where the general rule applies, zones are bounded by meridians at multiples of 6° (section 2-6.3.1).

Two things to be careful about:

- The text that came back reads "at the expense of zone 51". That is an error of the scanned text: zone 51 lies in east Asia, and only zone 31 borders zone 32 on the side that can give way. Read as 31.
- **The manual prints widths, not longitude limits.** The limits follow from the widths and the 6° rule: zone 31 from 0° to 3° E and zone 32 from 3° E to 12° E in the Norway band; zones 31, 33, 35, 37 from 0° to 9°, 9° to 21°, 21° to 33° and 33° to 42° E in the Svalbard band. This derivation is mine. The manual does not say whether a point exactly on 56°, 64° or 72° belongs inside or outside the band, so no question uses a point on or near a boundary.

**Cross-check.** The Python package `utm` 0.8.1 has a zone function that implements the exceptions. It gives the derived zone for all nine points below. It is used only as a check of my reading, not as the reference; if it is ever tested, these questions do not depend on it.

| Point | Zone by the 6° rule alone | Zone with the exceptions | What it tests |
|---|---|---|---|
| 60.4° N, 5.3° E | 31 | **32** | the Norway widening |
| 60.4° N, 2.0° E | 31 | 31 | the narrowed zone 31 still exists |
| 50.0° N, 5.3° E | 31 | 31 | outside the band, no exception |
| 70.0° N, 10.5° E | 32 | 32 | between the two bands, no exception |
| 78.2° N, 15.6° E | 33 | 33 | inside a widened Svalbard zone |
| 78.5° N, 10.5° E | 32 | **33** | zone 32 is not used there |
| 79.0° N, 7.0° E | 32 | **31** | zone 31 widened to 9° |
| 78.0° N, 25.0° E | 35 | 35 | inside a widened Svalbard zone |
| 80.0° N, 35.0° E | 36 | **37** | zone 36 is not used there |

**Found on the way, not a finding about any tool.** `pyproj.database.query_utm_crs_info` returns zone 31 for the first point and zone 32 for the sixth. That function lists the coordinate systems whose recorded area of use contains a point; it does not choose a zone, and its documentation does not claim to. An agent that used it to choose a zone would get the wrong one in these places. This is a remark for the write-up of the build, not something to report.

## 2. The area of a figure on the ellipsoid

**Source.** C. F. F. Karney, "Algorithms for geodesics", *Journal of Geodesy* 87 (2013) 43–55, https://doi.org/10.1007/s00190-012-0578-z. The article page states that it is open access under the Creative Commons Attribution License (version 2.0). Read verbatim from the journal's PDF: Tables 2, 3, 6 and 7. The author's addenda page (https://geographiclib.sourceforge.io/geod-addenda.html, dated 2022-06-08) was read in full; it lists no correction to any number in these tables.

Table 7 prints the area between the equator and the geodesic that starts at latitude 40° with azimuth 30° and runs 10 000 km on the WGS84 ellipsoid: **S12 = 84 275 623.422 35 km²**. Table 2 prints where that geodesic ends: latitude 41.793 310 205 06°, longitude difference 137.844 900 043 77°, azimuth 149.090 169 318 07°.

This area is the area of a quadrilateral whose corners can be stated: (0°, 0°), (40° N, 0°), (41.793 310 205 06° N, 137.844 900 043 77° E), (0°, 137.844 900 043 77° E). Its sides are the geodesic, two meridians and the equator, and each of those is itself a geodesic, so any tool that computes the area of a polygon with geodesic sides can be asked.

| | Area |
|---|---|
| Printed (Table 7) | 84 275 623.422 35 km² |
| GeographicLib, polygon with the corners above | −84 275 623.422 35 km² |
| PROJ, same polygon | −84 275 623.422 35 km² |

The minus sign is the programs' convention for corners listed clockwise. So a question on area has to state the order of the corners and accept the size of the area; whether a tool's sign means anything is a "must state" matter for format version 2, as with the grid convergence on 25 November.

## 3. The length of a line given as a list of points

No new source is needed. The length of a line through several points is the sum of the lengths of its legs; that is a definition, not a result that needs a table. So a question needs only legs whose lengths are printed. The Australian manuals print one: Flinders Peak to Buninyong, 54 972.271 m.

| Line | Reference | PROJ |
|---|---|---|
| Flinders Peak → Buninyong | 54 972.271 m (printed) | 54 972.2711 m |
| Flinders Peak → Buninyong → Flinders Peak | 109 944.542 m (twice the printed leg) | 109 944.5423 m |

The out-and-back line is chosen on purpose: the trial of 24 November found a server that doubled a line's length, and a line of two legs shows whether a tool counts a leg twice or not at all.

## 4. More printed examples from the same paper

Karney's paper also prints worked examples of the two main problems. They are harder cases than the Australian line, and they are useful for that reason.

| Example | Printed | Both programs |
|---|---|---|
| Table 2, direct: from 40° N, azimuth 30°, 10 000 000 m | end latitude 41.793 310 205 06°, longitude difference 137.844 900 043 77°, azimuth at end 149.090 169 318 07° | the same to every printed digit |
| Table 6, inverse, nearly antipodal: −30° to 29.9°, longitude difference 179.8° | azimuths 161.890 524 736 33° and 18.090 737 245 74°, distance 19 989 832.827 610 m | the same to every printed digit |
| Table 3, inverse, a short line: −30.123 45° to −30.123 44°, longitude difference 0.000 05° | azimuths 77.043 533 542 37° and 77.043 508 449 13°, distance 4.944 208 m | distance the same; **both azimuths 1.35 × 10⁻⁹ degree smaller**: 77.043 533 541 02° and 77.043 508 447 78° |

**The disagreement in Table 3 is not explained.** Both programs agree with each other to every digit and differ from the print in the tenth decimal place of a degree (about 5 millionths of a second of arc). I checked one possible cause: the input latitudes cannot be held exactly in binary floating point. That error is about 2 × 10⁻¹⁵ degree, and on this short line it moves the azimuth by about 5 × 10⁻¹⁰ degree in the wrong direction, so it does not account for the difference. The addenda page does not mention it. By the rule of 25 November (a number is used only where print and both computations agree), this example is used only to the digits that agree: azimuths to 10⁻⁸ degree, distance to 1 µm. It is not a finding against either program, and nothing is reported.

## Reuse terms

The DMA manual is approved for public release with unlimited distribution. Karney's article is under CC BY 2.0, which allows reuse with credit. The bench quotes single figures with their source, which both allow. No text is copied; the descriptions above are in my own words.

## What this changes

- The three kinds of question that were blocked now have sources: nine zone questions, one area question, two line-length questions, and three more worked examples of the direct and inverse problems from Karney's tables.
- What is still open: the boundaries of the Norway and Svalbard bands (not stated in the manual read), and a printed perimeter of a polygon (none found; not needed for the questions above).
- The build itself (new tasks in the format, a checker, adapters) is the next step in `PLAN.md`, after the round of 1 December.
