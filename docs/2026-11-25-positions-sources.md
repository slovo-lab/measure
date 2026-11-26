# Positions: the sources read, and the first questions

*Русская версия: [2026-11-25-positions-sources.ru.md](2026-11-25-positions-sources.ru.md)*

Written by Claude (AI) on 25 November 2026. The one-day trial of 24 November ([`pilots/coordinates`](../pilots/coordinates/README.md)) used numbers written from memory. This note replaces memory with sources, so that questions about positions can enter the bench. None of this is in the round of 1 December.

**How the sources were read.** Through a fetch tool that answers questions about a document's text; I did not see the pages. Each number below was asked for "exactly as printed" with its place in the document, and then recomputed by two independent programs (GeographicLib 2.1 and PROJ through pyproj 3.8.0). A number is used only where print and both computations agree.

## Source 1: the Australian manuals

- *Geocentric Datum of Australia Technical Manual*, version 2.4, 2 December 2014, Intergovernmental Committee on Surveying and Mapping (ICSM). https://icsm.gov.au/sites/default/files/2017-09/gda-v_2.4_0.pdf
- *Geocentric Datum of Australia 2020 Technical Manual*, version 1.2, 24 August 2018, ICSM. https://icsm.gov.au/sites/default/files/GDA2020TechnicalManualV1.1.1.pdf (the file name says 1.1.1; the title page says 1.2)

Both print the same line between two survey marks, on the GRS80 ellipsoid (a = 6 378 137 m, 1/f = 298.257222101):

| | Flinders Peak | Buninyong |
|---|---|---|
| Latitude | −37° 57′ 03.72030″ | −37° 39′ 10.15610″ |
| Longitude | 144° 25′ 29.52440″ | 143° 55′ 35.38390″ |
| Grid zone | 55 | 55 |
| Easting | 273 741.297 m | 228 854.052 m |
| Northing | 5 796 489.777 m | 5 828 259.038 m |
| Grid convergence | −1° 35′ 03.65″ | not printed |
| Point scale factor | 1.000 230 56 | not printed |

| Between them | As printed | Where |
|---|---|---|
| Ellipsoidal distance | 54 972.271 m | 2014 manual, chapter 4, p. 18; 2020 manual, section 5.1.3, table 5.1 |
| Forward azimuth | 306° 52′ 05.37″ | same |
| Reverse azimuth | 127° 10′ 25.07″ | same |
| Plane distance on the grid | 54 992.279 m | 2014 manual, chapter 6, p. 27 |
| Grid bearing | 305° 17′ 01.72″ | same |
| Arc-to-chord correction at Flinders Peak | +19.47″ | same |
| Line scale factor | 1.000 363 97 | same |

The grid coordinates are printed in the 2014 manual (chapters 5 and 6); the fetch tool found no worked grid example in the first two thirds of the 2020 manual. The grid is a transverse Mercator with central scale factor 0.9996, false easting 500 000 m, false northing 10 000 000 m and zones 6° wide (2014 manual, table 1-1; 2020 manual, table 1.8).

**Recomputed.** GeographicLib and PROJ both give 54 972.2711 m, 306° 52′ 05.373″ and 127° 10′ 25.070″. PROJ gives E 273 741.2966, N 5 796 489.7769 for Flinders Peak and E 228 854.0513, N 5 828 259.0384 for Buninyong, a convergence of 1° 35′ 03.647″ in size, a point scale factor of 1.000230559, a plane distance of 54 992.2792 m and a line scale factor of 1.000363967. Every printed figure agrees to its last digit. The straight-line bearing on the grid computes to 305° 17′ 21.19″, which is the printed grid bearing plus the printed arc-to-chord correction, as the manual's own definitions say it should be.

One thing to carry into the questions: the sign of the grid convergence. The manual prints −1° 35′ 03.65″; PROJ reports +1.584°. The two use opposite sign conventions. A question about convergence has to accept either sign only if the tool says which convention it uses, which is a case for the "must state" rule of format version 2.

## Source 2: the definition of the UTM grid

- *The Universal Grids: Universal Transverse Mercator (UTM) and Universal Polar Stereographic (UPS)*, DMA Technical Manual 8358.2, September 1989, Defense Mapping Agency. https://apps.dtic.mil/sti/pdfs/ADA266497.pdf

Read for the specification: transverse Mercator in zones 6° wide; zone 1 from 180°W to 174°W, numbers rising eastward to 60; central scale factor 0.9996; false easting 500 000 m; false northing 0 m in the northern hemisphere and 10 000 000 m in the southern; used between 80°S and 84°N (sections 2-2.2 and 2-3).

**Not found there: the exceptions over Norway and Svalbard.** The fetch tool reports that this manual says the zones are uniformly 6° wide and does not mention the widened zone 32. The exceptions belong to the grid-zone designations, which another manual of the same series (8358.1) defines; that one has not been read. So the question "which zone is Bergen in" stays out of the bench until it has a read source, however well known the answer is. A second copy of 8358.2 as plain text answered with a robot check and was left alone.

## Reuse terms

The 2020 manual is published under a Creative Commons Attribution 4.0 licence, the 2014 manual under Creative Commons Attribution 3.0 Australia (both as stated in the documents, seen in search excerpts). The DMA manual is marked "Approved for public release; distribution unlimited". The bench quotes single figures with their source, which all three allow.

## The first questions proposed

All on the printed line, so every answer has a printed value and two recomputations.

| Question | Reference | Tolerance proposed |
|---|---|---|
| Distance on the GRS80 ellipsoid from Flinders Peak to Buninyong | 54 972.271 m | 1 mm |
| Forward azimuth of that line | 306° 52′ 05.37″ | 0.01″ |
| Reverse azimuth | 127° 10′ 25.07″ | 0.01″ |
| The point 54 972.271 m from Flinders Peak at azimuth 306° 52′ 05.37″ | Buninyong, as printed | 0.0001″ in each coordinate (about 3 mm) |
| Flinders Peak on the grid of zone 55 south | E 273 741.297, N 5 796 489.777 | 1 mm |
| Buninyong on the same grid | E 228 854.052, N 5 828 259.038 | 1 mm |
| Grid coordinates of Flinders Peak back to latitude and longitude | as printed | 0.0001″ |
| Point scale factor at Flinders Peak | 1.000 230 56 | 1e-8 |
| Grid convergence at Flinders Peak | 1° 35′ 03.65″ in size; the tool must say which sign convention it uses | 0.01″ |
| Relation: distance there equals distance back | equal | 1e-9 m |
| Relation: to the grid and back returns the starting point | equal | 1e-9 degree |

Two of the trial's findings are not covered by a printed value and need their own sources before they become questions: the area of a figure on the ellipsoid (GeographicLib is a reference implementation, not a printed table), and the length of a line given as a list of points.

## What has to be built

1. New tasks in the format: a line between two points (inverse), a point from a start, an azimuth and a distance (direct), to the grid, from the grid. Angles are given in degrees, minutes and seconds as printed and compared in seconds.
2. A checker that recomputes these references. The existing one uses exact fractions; these need a second independent implementation, and the rule should be the one used above: print and two programs agree.
3. Adapters: the libraries first (PROJ through pyproj, GeographicLib), then the three servers of the trial.

Earliest round: 4 January 2027, if built and announced by 29 December.

---

*Note added 26 November 2026:* the three kinds of question this note left without a source (zone exceptions, area, a line of points) now have one: see [`2026-11-26-positions-remaining-sources.md`](2026-11-26-positions-remaining-sources.md).
