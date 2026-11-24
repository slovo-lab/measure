# Measure: results

Run on 2026-11-24 with Python 3.13.18. This file is written by `tools/make_results.py`; do not edit it by hand.

Each tool was given the 43 reference pairs in [`pairs/pairs.json`](pairs/pairs.json). A pair passes when every answer is within the tolerance stated in the pair. Most tolerances only allow for ordinary double-precision arithmetic; the exceptions are explained in [`FORMAT.md`](FORMAT.md).

## Versions tested

- **Pint + uncertainties**: numpy 2.5.5, pint 0.26.2, uncertainties 3.2.3
- **ucon**: ucon 2.4.2
- **ucon-mcp (server)**: mcp 1.30.0, ucon 2.4.2, ucon-tools 0.13.0
- **unit-converter-mcp (server)**: mcp 1.30.0, unit-converter-mcp 0.1.2
- **mcp-units (server)**: mcp 1.30.0, mcp-units 0.1.0, pint 0.26.2
- **mcp-gnu-units (server)**: GNU units data 3.26, mcp-gnu-units 0.1.1
- **measurement-uncertainty-mcp (server)**: mcp 1.30.0, measurement-uncertainty-mcp 0.1.0

## Summary

| Category | Pairs | Pint + uncertainties | ucon | ucon-mcp (server) | unit-converter-mcp (server) | mcp-units (server) | mcp-gnu-units (server) | measurement-uncertainty-mcp (server) |
|---|---|---|---|---|---|---|---|---|
| Unit conversion | 19 | 19 of 19 pass | 17 of 17 pass, 2 not offered | 17 of 17 pass, 2 not offered | 17 of 17 pass, 2 not offered | 19 of 19 pass | 19 of 19 pass | not offered (19) |
| Dimensional safety | 5 | 5 of 5 pass | 5 of 5 pass | 1 of 1 pass, 4 not offered | 1 of 1 pass, 4 not offered | 1 of 1 pass, 4 not offered | 1 of 1 pass, 4 not offered | not offered (5) |
| Combined uncertainty | 8 | 8 of 8 pass | 5 of 6 pass, 2 not offered | not offered (8) | not offered (8) | not offered (8) | not offered (8) | not offered (8) |
| Type A evaluation | 2 | not offered (2) | not offered (2) | not offered (2) | not offered (2) | not offered (2) | not offered (2) | 2 of 2 pass |
| Type B evaluation | 4 | not offered (4) | not offered (4) | not offered (4) | not offered (4) | not offered (4) | not offered (4) | 2 of 2 pass, 2 not offered |
| Degrees of freedom | 2 | not offered (2) | not offered (2) | not offered (2) | not offered (2) | not offered (2) | not offered (2) | 2 of 2 pass |
| Reporting | 3 | not offered (3) | not offered (3) | not offered (3) | not offered (3) | not offered (3) | not offered (3) | not offered (3) |
| **All** | 43 | 32 of 32 pass, 11 not offered | 27 of 28 pass, 15 not offered | 18 of 18 pass, 25 not offered | 18 of 18 pass, 25 not offered | 20 of 20 pass, 23 not offered | 20 of 20 pass, 23 not offered | 6 of 6 pass, 37 not offered |

"Not offered" means the tool has no function for that kind of task (the runner's verdict `unsupported`). It is not counted as a failure.

## What this does and does not show

- It shows how each tool answered these 43 questions on this date, with these versions.
- It does not rank the tools, and a pass here does not certify a tool for any use.
- Tools marked "(server)" were started as servers for AI agents and called through their tools, the way an agent calls them. The others were called as Python libraries.
- Categories with no pairs yet: none.

## Every answer that was not a pass

### ucon: `comb-square-same-variable` (fail)

- `combined_standard_uncertainty`: reference 0.04 m^2, tool gave 0.0282842712474619; relative difference -0.293

## Notes on this run

These notes were written by hand (by Claude, an AI) after looking at each answer that was not a pass. They are kept in `results/2026-11-24-notes.md`.

### ucon and `comb-square-same-variable`

The pair states the model as `s * s`, with one measured quantity `s`. ucon 2.4.2 returns 0.0283 m^2, the value for two independent measurements; the reference is 0.04 m^2. When the same model is written as `s ** 2` (pair `comb-square-as-power`), ucon returns the reference value. So the difference is in how ucon treats a number multiplied by itself, not in its handling of powers. We have not checked whether ucon's documentation describes this.

To reproduce:

```python
from ucon import Number, parse_unit
s = Number(2.0, parse_unit("m"), uncertainty=0.01)
print(s * s)    # 4.0 ± 0.0282842712474619 m²
print(s ** 2)   # 4.0 ± 0.04 m²
```

### An observation outside the pairs: the spelling `nmi` in ucon

Our pairs file writes the nautical mile as `nmi`. ucon 2.4.2 accepts that spelling but reads it as nano-mile (prefix `n` and unit `mi`), and its answers then depend on the target unit:

```python
from ucon import parse
print(parse("1 nmi").to("m"))     # 1852.0 m          (nautical mile)
print(parse("10 nmi").to("km"))   # 1.609344e-08 km   (nano-mile)
```

ucon's own name for the unit is `nautical_mile`, and with that name the pair `conv-nautical-mile-km` passes. An adapter's job is to translate our spellings into the tool's own, so the adapter uses `nautical_mile` and the pair is recorded as a pass. The behaviour of `nmi` is noted here because a user or an AI agent could type it and get a number without any warning.

### Ten pairs added after version 0.1.0

The run was repeated the same day with 43 pairs. Of the ten new pairs, the two libraries were asked only the three they have functions for; both refused to convert kilograms to metres, as they should. Pint converted both temperature differences correctly. In ucon 2.4.2 we found no unit for a temperature difference, so those two pairs are "not offered" there; we looked in the package, not in ucon's online documentation. Neither library has a function for effective degrees of freedom, for rounding to significant digits, or for a Type B evaluation, so the other seven pairs are "not offered" for both. Those pairs are there for the tools that do offer such functions and have not been tested yet.

### The servers for AI agents

Two tools were also tested the way an AI agent uses them: started as servers and called through their tools. Both `ucon-mcp` and `unit-converter-mcp` passed every conversion pair they have a tool for, and both turned down the request to convert a mass into a length. Neither has a tool for adding quantities or for uncertainty, so those pairs are marked "not offered".

Two more unit servers were added later the same day: `mcp-units` (built on Pint, installed from its repository at commit `913fee9` with the owner's approval) and `mcp-gnu-units` 0.1.1 (built on the GNU units database). Both passed all 20 conversion pairs, including the two temperature differences that the first two servers have no unit for, and both refused to convert a mass into a length.

Another server, `measurement-uncertainty-mcp`, covers the other half of the reference set: it has no units, and it has tools for Type A and Type B evaluation and for effective degrees of freedom. It passed all 6 pairs it has a tool for. It is not on the Python package index, so it was installed from its repository at commit `fe254e0`; the lab's owner approved running it. Two kinds of pair were not put to it, to keep the adapter from doing the calculation itself: Type B with a normal distribution (the tool wants a coverage factor, the pair gives a coverage probability) and propagation through a model (one tool needs the sensitivity coefficients from the caller, the other answers by random sampling, which is a different method from the one our references use).

So far no server for AI agents has been found that takes a measurement model and returns the first-order combined uncertainty. The eight pairs in that category can only be run against the Python libraries.

One detail: the server `ucon-mcp` converts `10 nmi` to 18.52 km, the right answer, while the ucon library called directly gives the nano-mile answer described above. The adapter sends `nautical_mile` in both cases; the `nmi` spelling was tried by hand.

### Reporting to the authors

Under this project's fairness rule, both points were reported to ucon's authors on 24 November 2026: [issue 395](https://github.com/withtwoemms/ucon/issues/395) (`nmi`) and [issue 396](https://github.com/withtwoemms/ucon/issues/396) (`x * x`). The text is in [`reports/2026-11-24-ucon.md`](reports/2026-11-24-ucon.md).

## All results

| Pair | Pint + uncertainties | ucon | ucon-mcp (server) | unit-converter-mcp (server) | mcp-units (server) | mcp-gnu-units (server) | measurement-uncertainty-mcp (server) |
|---|---|---|---|---|---|---|---|
| `conv-inch-mm` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-pound-kg` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-kmh-ms` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-kwh-j` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-degc-k` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-degf-degc` | pass | pass | pass | pass | pass | pass | not offered |
| `typea-mean-five-readings` | not offered | not offered | not offered | not offered | not offered | not offered | pass |
| `typeb-rectangular-half-width` | not offered | not offered | not offered | not offered | not offered | not offered | pass |
| `comb-product-uncorrelated` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `comb-sum-with-covariance` | pass | not offered | not offered | not offered | not offered | not offered | not offered |
| `dim-add-length-time` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `conv-foot-m` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-mile-km` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-mph-ms` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-nautical-mile-km` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-litre-m3` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-atm-kpa` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-bar-pa` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-calth-j` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-sqin-mm2` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-degf-k` | pass | pass | pass | pass | pass | pass | not offered |
| `conv-min-h` | pass | pass | pass | pass | pass | pass | not offered |
| `dim-add-length-mass` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `dim-add-voltage-current` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `dim-add-foot-inch` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `comb-quotient-uncorrelated` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `comb-difference-with-covariance` | pass | not offered | not offered | not offered | not offered | not offered | not offered |
| `comb-square-same-variable` | pass | fail | not offered | not offered | not offered | not offered | not offered |
| `comb-product-mixed-units` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `comb-linear-combination` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `typea-mean-four-readings` | not offered | not offered | not offered | not offered | not offered | not offered | pass |
| `typeb-triangular-half-width` | not offered | not offered | not offered | not offered | not offered | not offered | pass |
| `comb-square-as-power` | pass | pass | not offered | not offered | not offered | not offered | not offered |
| `conv-degf-interval-k` | pass | not offered | not offered | not offered | pass | pass | not offered |
| `conv-degc-interval-k` | pass | not offered | not offered | not offered | pass | pass | not offered |
| `dim-convert-mass-length` | pass | pass | pass | pass | pass | pass | not offered |
| `typeb-normal-9973-limits` | not offered | not offered | not offered | not offered | not offered | not offered | not offered |
| `typeb-normal-95-interval` | not offered | not offered | not offered | not offered | not offered | not offered | not offered |
| `dof-welch-satterthwaite-two` | not offered | not offered | not offered | not offered | not offered | not offered | pass |
| `dof-welch-satterthwaite-three` | not offered | not offered | not offered | not offered | not offered | not offered | pass |
| `round-half-odd-goes-up` | not offered | not offered | not offered | not offered | not offered | not offered | not offered |
| `round-half-even-stays` | not offered | not offered | not offered | not offered | not offered | not offered | not offered |
| `round-above-half-goes-up` | not offered | not offered | not offered | not offered | not offered | not offered | not offered |

Every number behind this table is in [`results/2026-11-24.json`](results/2026-11-24.json).
