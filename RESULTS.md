# Measure: results

Run on 2026-11-24 with Python 3.13.18. Written by a program; see `tools/run_bench.py`.

Each tool was given the 33 reference pairs in [`pairs/pairs.json`](pairs/pairs.json). A pair passes when every answer is within the tolerance stated in the pair. The tolerances only allow for ordinary double-precision arithmetic.

## Versions tested

- **Pint + uncertainties**: Pint 0.26.2, numpy 2.5.5, uncertainties 3.2.3
- **ucon**: ucon 2.4.2

## Summary

| Category | Pairs | Pint + uncertainties | ucon |
|---|---|---|---|
| Unit conversion | 17 | 17 of 17 pass | 17 of 17 pass |
| Dimensional safety | 4 | 4 of 4 pass | 4 of 4 pass |
| Combined uncertainty | 8 | 8 of 8 pass | 5 of 6 pass, 2 not offered |
| Type A evaluation | 2 | not offered (2) | not offered (2) |
| Type B evaluation | 2 | not offered (2) | not offered (2) |

"Not offered" means the tool has no feature for that kind of task. It is not counted as a failure.

## What this does and does not show

- It shows how each tool answered these 33 questions on this date, with these versions.
- It does not rank the tools, and a pass here does not certify a tool for any use.
- The tools were called through their Python interfaces. Servers that wrap them for AI agents were not tested.
- Categories with no pairs yet: Degrees of freedom, Reporting.

## Every answer that was not a pass

### ucon: `comb-square-same-variable` (fail)

- `combined_standard_uncertainty`: reference 0.04 m^2, tool gave 0.0282842712474619; relative difference 0.293

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

ucon's own name for the unit is `nautical_mile`, and with that name the pair `conv-nautical-mile-km` passes. An adapter's job is to translate our spellings into the tool's, so the adapter uses `nautical_mile` and the pair is recorded as a pass. The behaviour of `nmi` is noted here because a user or an AI agent could type it and get a number without any warning.

### Reporting to the authors

Under this project's fairness rule, both points are to be reported to ucon's authors. The proposed text is in [`reports/2026-11-24-ucon.md`](reports/2026-11-24-ucon.md). It is sent only after the lab's owner confirms, because it is a post on an outside platform.

## All results

| Pair | Pint + uncertainties | ucon |
|---|---|---|
| `conv-inch-mm` | pass | pass |
| `conv-pound-kg` | pass | pass |
| `conv-kmh-ms` | pass | pass |
| `conv-kwh-j` | pass | pass |
| `conv-degc-k` | pass | pass |
| `conv-degf-degc` | pass | pass |
| `typea-mean-five-readings` | not offered | not offered |
| `typeb-rectangular-half-width` | not offered | not offered |
| `comb-product-uncorrelated` | pass | pass |
| `comb-sum-with-covariance` | pass | not offered |
| `dim-add-length-time` | pass | pass |
| `conv-foot-m` | pass | pass |
| `conv-mile-km` | pass | pass |
| `conv-mph-ms` | pass | pass |
| `conv-nautical-mile-km` | pass | pass |
| `conv-litre-m3` | pass | pass |
| `conv-atm-kpa` | pass | pass |
| `conv-bar-pa` | pass | pass |
| `conv-calth-j` | pass | pass |
| `conv-sqin-mm2` | pass | pass |
| `conv-degf-k` | pass | pass |
| `conv-min-h` | pass | pass |
| `dim-add-length-mass` | pass | pass |
| `dim-add-voltage-current` | pass | pass |
| `dim-add-foot-inch` | pass | pass |
| `comb-quotient-uncorrelated` | pass | pass |
| `comb-difference-with-covariance` | pass | not offered |
| `comb-square-same-variable` | pass | fail |
| `comb-product-mixed-units` | pass | pass |
| `comb-linear-combination` | pass | pass |
| `typea-mean-four-readings` | not offered | not offered |
| `typeb-triangular-half-width` | not offered | not offered |
| `comb-square-as-power` | pass | pass |

Full numbers for every answer are in [`results/2026-11-24.json`](results/2026-11-24.json).
