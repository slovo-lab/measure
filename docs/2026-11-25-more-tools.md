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
