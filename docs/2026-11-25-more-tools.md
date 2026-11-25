# More tools the bench could test

*Русская версия: [2026-11-25-more-tools.ru.md](2026-11-25-more-tools.ru.md)*

Written by Claude (AI) on 25 November 2026, after the lab's owner asked whether there is anyone else to test. Short answer: yes, at least a dozen. The list was made by asking the package indexes for names and by two web searches. Seven libraries were then installed and asked a handful of the bench's questions **by hand, with no adapter**. That is a first look, not a result: nothing below has been through the runner, and nothing has been reported to anyone.

## Tried by hand (seven libraries)

Questions: inch to millimetre, pound to kilogram, nautical mile to metre, calorie to joule, 77 °F to °C, adding 5 m and 3 s, and, where the library has uncertainty, the square of s = 2.000 m ± 0.010 m written as `s * s` and as `s ** 2`.

| Tool | Version | Kind | First look |
|---|---|---|---|
| MetroloPy | 1.1.1 (Python) | units and uncertainty by the GUM, from a metrologist's hand | All right, with exact fractions where the factor is exact; refuses m + s; `s * s` and `s ** 2` both give 0.04. The closest relative of what Measure asks. |
| astropy.units | 8.0.3 (Python) | units | All right (25.400000000000002 mm for the inch, inside the tolerance); refuses m + s. |
| unyt | 3.2.0 (Python) | units | All right; refuses m + s. |
| quantities | 0.17.0 (Python) | units, with an "uncertain quantity" | Conversions right; refuses m + s. **`s * s` gives 0.0283 and `s ** 2` gives 0.04**: the same disagreement the bench found in ucon. To be confirmed through the runner, and its documentation read, before anything is said to its authors. |
| mathjs | 15.3.0 (JavaScript) | units inside a general mathematics library | Right where it has the unit; no unit named `nmi` or `cal`. |
| js-quantities | 1.8.0 (JavaScript) | units | Mostly right. **US gallon to litre gives 3.7854118; the exact value is 3.785411784**, a relative difference of 4e-9, outside the bench's tolerance for exact factors. To be confirmed through the runner. |
| unitpy | 0.0.19 (Python) | units | **Does not import after a fresh install** (`No module named 'pkg_resources'`). |

physipy 0.2.8 was installed too; its unit names were not found in the time given, so nothing is said about it.

## Found, not tried

| Tool | Where | Why it belongs |
|---|---|---|
| Suncal 1.7.1 | Python package index; Sandia National Laboratories | Uncertainty by the GUM and Monte Carlo, Type A and B; already on the metrologists list. |
| METAS UncLib 3.0.3 | Python package index; METAS | A national institute's uncertainty library. Its licence forbids redistribution; read it before running it in public tests. |
| unit-converter-ai-mcp 1.0.11 | Python package index | A server for agents: length, weight, temperature. |
| mcp-units 0.3.3 | Python package index (a different project from the `mcp-units` the bench installs from a repository) | A server for agents with cooking units. The two share a name; the reports must keep them apart. |
| metroai | repository of the author of measurement-uncertainty-mcp | A larger project around the same uncertainty server. The hosted version needs an account and is not for the bench; a local install might be. |
| convert-units 2.3.4, convert 8.2.0 | JavaScript package index | Widely used unit converters for programs; agents reach them through code. |
| SymPy 1.14.0 (`sympy.physics.units`), uncertainties 3.2.3 alone | Python | Already in wide use; SymPy has its own unit system. |
| General calculator servers (mcp-server-calculator, calculator-mcp, mcp-calculator, math-mcp, mcp-scientific-calculator) | Python package index | To look at: whether any of them converts units. If not, they are outside the bench. |

## What this means

1. There is a second ring of tools: mature libraries that programs, and so agents that write programs, use every day. The bench has so far looked mostly at servers.
2. JavaScript tools need one new piece: an adapter that starts a Node program. Nothing else in the bench cares about the language.
3. None of these can join the round of 1 December, whose list of tools was announced. They can join the round of 4 January if their adapters exist by the announcement on 29 December.
4. Order proposed: MetroloPy and quantities first (both have uncertainty, and one shows a likely finding), then astropy and unyt (cheap), then the JavaScript adapter with mathjs and js-quantities, then Suncal.

## Later the same day: two of them through the runner

Adapters were written for MetroloPy and quantities (`bench/adapters/metrolopy_adapter.py`, `quantities_adapter.py`), and the 43 published pairs were put to both. They are not in the round of 1 December, whose tools were announced before; they wait for the round of 4 January.

| Tool | Pass | Fail | Not offered | What failed |
|---|---|---|---|---|
| MetroloPy 1.1.1 | 40 | 0 | 3 | Nothing. The three it does not offer are the rounding pairs. It is the first tool to answer every other question: conversions, Type A, Type B for three distributions, propagation with covariance, effective degrees of freedom. |
| quantities 0.17.0 | 24 | 4 | 15 | `s * s` gives a combined uncertainty of 0.0283 where 0.04 is right (and `s ** 2` gives 0.04). And three temperature conversions: 25 °C to kelvin gives 25, 98.6 °F to °C gives 54.78, −40 °F to kelvin gives −22.2. The package treats degrees as intervals and applies no offset. |

**Before anything is said to the authors of quantities, its documentation has to be read.** Both behaviours may be stated there as known limits; if so, they are limits of the tool that the bench shows, not defects to report. Either way an agent that calls the package gets these numbers.

*Corrected the same afternoon: see the section "Afternoon of 25 November" at the end. The three temperature failures of quantities were the adapter's mistake.*

## More servers tried by hand

| Tool | Version | First look |
|---|---|---|
| unit-converter-ai-mcp | 1.0.11 | **Does not start after a fresh install** (the `mcp` 2.x cause again). With `mcp<2`: inch to mm right; **1 lb = 0.453592 kg where the exact value is 0.45359237**, a relative difference of 8e-7; unit names are fixed words (`inch`, not `in`). To be confirmed through an adapter. |
| mcp-units (package index, cooking units) | 0.3.3 | **Does not start after a fresh install**: an import error between its pinned `mcp` 1.15.0 and the current pydantic. Not looked at further. |
| p6plab-mcp-calculator | 2.0.1 | Starts. 70 tools, among them `convert_units`. Not asked anything yet. |

Found by search, not installed: Phys-MCP (a physics server with `units_convert`), CalcsLive (unit-aware engineering calculations, hosted; needs an account, so not for the bench), two calculator servers that live only in repositories (running code from a repository needs the owner's approval each time).

## What several tools take a bare unit name to mean

Asked by hand: Pint, GNU units (through its server), MetroloPy, quantities, mathjs, js-quantities.

| Asked for | All of them answered with | The other reading in daily use |
|---|---|---|
| calorie | 4.184 J (thermochemical) | 4.1868 J (International Table) |
| gallon | 3.785 L (US) | 4.546 L (imperial) |
| pint | 0.473 L (US liquid) | 0.568 L (imperial) |
| ton | 907 kg (US short ton) | 1016 kg (long ton), 1000 kg (tonne) |

Every tool chose the United States reading, and none said so in its answer. They agree with each other, so no tool is wrong against another. An agent answering someone in Britain would be wrong by 20% on a pint. See the decision in `FORMAT.md`.

## Afternoon of 25 November: a correction, and three more through the runner

**A correction about quantities.** Its documentation was read (the page "Known Issues"). It says that the package treats temperatures as temperature differences, and that Celsius and Fahrenheit scales would need an offset that its conversions do not support. So the three "failed" temperature conversions in the table above were the adapter's mistake: it handed a temperature to a unit that the package documents as a difference. The adapter now reports temperatures as not offered and uses the package's `degC` where the pair means a difference. The corrected line: **26 pass, 1 fail, 16 not offered**. What an agent should know stays true: the package answers 25 for "25 °C in kelvin" without an error.

The one failure left is `s * s`: combined uncertainty 0.0283 where 0.04 is right, and `s ** 2` gives 0.04. The package has no way to state that two inputs are correlated, and no page was found that says a variable multiplied by itself is treated as two independent ones. This is a candidate for a report; the lab's owner decides.

| Tool | Pass | Fail | Not offered | Notes |
|---|---|---|---|---|
| js-quantities 1.8.0 (JavaScript) | 24 | 0 | 19 | Every conversion and addition right to 1e-12, every refusal made. It keeps temperatures (`tempC`) and differences (`degC`) apart by name. |
| mathjs 15.3.0 (JavaScript) | 20 | 0 | 23 | Right on all it offers. No unit for the nautical mile, the calorie, or a temperature difference. |
| p6plab-mcp-calculator 2.0.1 (server) | 1 | 2 | 40 | See below. |

The JavaScript tools are asked through a small Node program (`bench/adapters/node/ask.js`) that, like every adapter, does no arithmetic.

**p6plab-mcp-calculator**, a server with 70 tools:

- `round`: 2.675 to two decimal places gives **2.67**. Every rounding rule gives 2.68 (the discarded part is exactly 5 and the kept digit is odd). 2.665 also gives 2.67, where the rule of NIST SP 811 gives 2.66. The server rounds the binary number nearest to what was typed, not the decimal number that was typed; sending the number as text changes nothing.
- `convert_units`: every request is answered with `"success": true` and the text "Unit conversion not yet implemented". The tool is in the list an agent sees. The runner records these pairs as not offered and quotes the server.
- It has `mean` and `std_dev` (the sample one) but nothing that gives the standard uncertainty of a mean.

**unit-converter-ai-mcp is not for the bench.** After the hand questions of this morning it answered: "Rate limit reached (10/day on free tier)", with a link to pay. Ten answers a day are fewer than one run of the pairs, the lab spends no money, and a limit is not something to work around. What was seen by hand stays in the table above as seen by hand.

**One more look at js-quantities.** By hand in the morning it gave a US gallon as 3.7854118 L, the exact value being 3.785411784. The published pairs have no gallon, so the runner did not ask. A pair for the gallon needs a read source first.

## Second correction, 25 November, 13:30: `q*q` in quantities is documented too

The paragraph above says no page was found that describes `s * s`. That was wrong, and the search had been too shallow: it looked at the "Known Issues" page only. The package's tutorial, which is the text inside the package itself, shows `q*q` next to `q**2` as an example, calls the first result "probably incorrect", and warns that correlations between operands are never taken into account, even when an operand is combined with itself. So this is a documented limit and is **not** a candidate for a report. The line in the results stays (26 pass, 1 fail), with this note.

**p6plab-mcp-calculator has no public tracker.** The repository named in its metadata answers "page not found". Under [`REPORTING.md`](../REPORTING.md) the report on its rounding and on its placeholder conversion tool would go by e-mail to the address in the metadata, if the lab's owner agrees to the text.

## Evening work, 25 November: astropy, unyt, and three questions about bare unit names

| Tool | Pass | Fail | Not offered | Notes |
|---|---|---|---|---|
| unyt 3.2.0 | 24 | 0 | 19 | Right on all it offers; keeps temperatures and differences apart (`degC`, `delta_degC`). |
| astropy.units 8.0.3 | 22 | 0 | 21 | Right on all it offers. Temperatures need the equivalency its documentation names; the adapter passes it. |

Both wait for the round of 4 January.

**Three new questions** in `pairs/proposed-v2.json`, each with every reading in daily use and a read source (NIST Handbook 44, Appendix C; NIST SP 811, Appendix B.8): "1 gallon in litres" (US 3.785411784, imperial 4.54609), "1 pint in litres" (US liquid 0.473176473, imperial 0.56826125, US dry 0.5506104713575), "1 ton in kilograms" (short 907.18474, long 1016.0469088, metric 1000). All values are exact.

| Tool | gallon | pint | ton |
|---|---|---|---|
| Pint 0.26.2 | US, unsaid | US liquid, unsaid | short, unsaid |
| ucon 2.4.2 | US, unsaid | US liquid, unsaid | no unit named ton |
| MetroloPy 1.1.1 | US, unsaid | US liquid, unsaid | no unit named ton |
| quantities 0.17.0 | US, **and says so** (`US_liquid_gallon`) | US liquid, unsaid | no unit named ton |
| mathjs 15.3.0 | US, unsaid | US liquid, unsaid | short, unsaid |
| unyt 3.2.0 | no such unit | no such unit | short, unsaid |
| astropy.units 8.0.3 | **3.7854117891** | **0.47317647364** | short, unsaid |
| js-quantities 1.8.0 | **3.7854118** | **0.473176475** | short, unsaid |

No tool gave the imperial reading, and none declined. Not offering a bare "ton" at all (three tools) is a sound answer to an unclear word.

**Two findings.** The numbers in bold are no reading of the unit:

- astropy defines the gallon as one litre divided by 0.264172052, a rounded factor. Its US gallon is 1.4 parts in a billion larger than 231 cubic inches. Quart, pint, cup, fluid ounce, tablespoon and teaspoon are derived from it.
- js-quantities defines the gallon as 0.0037854118 cubic metres and the pint as 0.000473176475, both rounded; 4 parts in a billion.

For most uses the difference does not matter. Both libraries give the inch, the pound and the mile exactly, and the gallon is exact by definition too. Existing issues were searched: astropy has none about the gallon's value; js-quantities has an open one about precision in comparisons (132) that does not name the rounded definitions. Both were reported the same day after the owner's yes: astropy issue 20948, js-quantities issue 153.

## Servers asked the same three questions (25 November, afternoon)

Four server adapters now report what the server's reply says about units, so the questions with several readings can be put to them. Their results on the 43 published pairs did not change.

| Server | calorie | gallon | pint | ton |
|---|---|---|---|---|
| ucon-mcp | thermochemical, unsaid | US, unsaid | US liquid, unsaid | **declines**, and names `metric_ton` and `short_ton` |
| unit-converter-mcp | thermochemical, unsaid | US, unsaid | US liquid, unsaid | **declines**: its list has "short ton (US)", "long ton (UK)", "tonne" and no bare "ton" |
| mcp-units | thermochemical, unsaid | US, unsaid | US liquid, unsaid | short, unsaid |
| mcp-gnu-units | thermochemical, unsaid | US, unsaid | US liquid, unsaid | short, unsaid |

All numbers are exact. Two servers handle "ton" the way a careful person would: they do not guess, and their reply shows the choices. That is counted as a pass. A library that only says "unknown unit" is counted as not offering the unit, because its reply does not show what it has instead (written into `FORMAT.md`).

Across all twelve tools asked: "gallon" was read as the US gallon by every tool that knows the word, and one (quantities) said so. No tool gave or mentioned the imperial gallon unasked.

## Suncal and convert-units (25 November, late afternoon)

| Tool | Pass | Fail | Not offered | Notes |
|---|---|---|---|---|
| Suncal 1.7.1 (Sandia National Laboratories) | 16 | 0 | 27 | Every uncertainty question right: Type A, Type B for three distributions, propagation with and without covariance, a variable multiplied by itself, effective degrees of freedom. It leaves units to Pint and has no conversion of its own. |
| convert-units 2.3.4 (JavaScript) | 10 | 5 | 28 | See below. |

Seventeen tools now. Both wait for the round of 4 January.

**convert-units** gives 1 inch as 25.3999991872 mm. The five failures:

| Asked | Came back | Exact | Relative difference |
|---|---|---|---|
| 1 in to mm | 25.3999991872 | 25.4 | 3.2e-8 |
| 6 ft to m | 1.82879994148 | 1.8288 | 3.2e-8 |
| 26.2 mi to km | 42.1648114507 | 42.1648128 | 3.2e-8 |
| 150 lb to kg | 68.0388 | 68.0388555 | 8.2e-7 |
| 2 in² to mm² | 1290.32124870 | 1290.32 | 9.7e-7 |

The cause is in the library's definitions: metric and imperial units are joined by one stored ratio per kind of quantity, and the ratios are rounded: 3.28084 feet per metre (exact: 1/0.3048), 453.592 grams per pound (exact: 453.59237), 10.7639 square feet per square metre. On the bare-word questions it gives a gallon of 3.7854117954 L and a ton of 907.184 kg, which match no reading. Temperatures, metric conversions and the refusal are right.

What the checks found. The README shows `convert(1).from('lb').to('kg')` with the comment "0.4536... (tested to 4 significant figures)", so the authors say how far imperial-to-metric results are tested. An earlier report of the area ratio (issue 281) was closed as completed. The beta of version 3 (3.0.0-beta.8, tried by hand) has the pound exact and the length, area and volume ratios unchanged. Nobody has reported the length ratio. The lab's owner was shown both sides and the text, and the length ratio was reported: convert-units issue 375.
