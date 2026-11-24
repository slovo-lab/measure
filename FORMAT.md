# Reference pairs: data format

Written by Claude (AI). Format version 1, 24 November 2026.

A reference pair is one question with a known answer and the source of that answer. All pairs live in one file, [`pairs/pairs.json`](pairs/pairs.json). The file is plain JSON so that any language can read it without extra libraries.

## Rules

1. **Every answer has a source a reader can check.** A source names a document, a place inside it (section, table row, equation number) and the date we looked. The `derivation` field shows the arithmetic from the source to the answer.
2. **No answer comes from a tool under test.** The answers are recomputed in `tests/test_pairs.py` with exact fractions from the Python standard library, using the formula in the cited source.
3. **Numbers are written as strings**: `"25.4"`, `"-40"`, `"1e-9"`, or a fraction such as `"250/9"`. A JSON number would be read as binary floating point, and `0.1` would already be inexact before any tool saw it.
4. **Nothing is copied from the sources.** Questions and input data are written for this project. Only facts (conversion factors, formulas) and their locations are taken from the sources.

## Top level

```json
{ "format_version": 1, "pairs": [ ... ] }
```

## One pair

| Field | Meaning |
|---|---|
| `id` | Lower-case words joined by hyphens. Never reused or changed once published. |
| `category` | One of `unit-conversion`, `dimensional-safety`, `type-a`, `type-b`, `combined`, `degrees-of-freedom`, `reporting`. |
| `question` | The task in plain words, complete in itself. This is what an AI agent would be asked. |
| `task` | The kind of calculation: `convert`, `type_a`, `type_b`, `propagate` or `add`. It fixes the shape of `inputs` and the names of the outputs. |
| `inputs` | The same data as in the question, in machine-readable form. See below. |
| `reference` | The expected result. See below. |
| `sources` | One or more sources: `document`, `locator`, optional `url`, and `checked` (the date we read it, `YYYY-MM-DD`). |
| `derivation` | The arithmetic from the source to the answer, in words a reader can follow with a pocket calculator. |

## Tasks

| `task` | `inputs` | Output names |
|---|---|---|
| `convert` | `value`, `unit`, `to_unit` | `value` |
| `type_a` | `readings` (list), `unit` | `mean`, `standard_uncertainty` (of the mean) |
| `type_b` | `distribution` (`rectangular` or `triangular`), `half_width`, `unit` | `standard_uncertainty` |
| `add` | `terms` (list of two or more, each with `value`, `unit`) | `value`, or a refusal when the terms are not of the same kind |
| `propagate` | `model` (an expression such as `V * I`), `variables` (each with `value`, `standard_uncertainty`, `unit`), `covariances` (list, may be empty; each with `between`, `value`, `unit`) | `value`, `combined_standard_uncertainty` |

In `propagate`, the reference is the first-order result of the law of propagation of uncertainty, because that is what the cited equation defines. Correlation is given as a covariance, the quantity that appears in that equation.

More tasks will be added when the first pair that needs them is written, and the format version will go up if an existing field changes meaning.

## Reference

```json
"reference": { "outputs": [
  { "name": "value", "value": "25.4", "unit": "mm", "exact": true,
    "tolerance": { "kind": "relative", "value": "1e-12" } }
] }
```

- `exact: true` means the stated value is the whole answer. `exact: false` means it is rounded to 12 significant digits.
- `tolerance` says how far a tool's answer may be from the reference and still pass: `relative` (a fraction of the reference value) or `absolute` (in the output unit). The tolerances in version 1 only allow for ordinary double-precision arithmetic: `1e-12` for exact answers and `1e-9` for rounded ones. They are not a judgment about how much error is acceptable in practice.
- A pair where the correct behaviour is to refuse (for example, adding a length to a time) has `"reference": { "outcome": "refuse" }` and no outputs. A tool passes if it reports an error or declines, and fails if it returns any number. The first such pair, `dim-add-length-time`, was added on 24 November 2026. The pair `dim-add-foot-inch` is the opposite control: a sum of two lengths in different units, which has an answer, so that a tool cannot pass this category by refusing every sum.

## Units

Units are written in plain ASCII: `mm`, `in`, `lb`, `kg`, `km/h`, `m/s`, `kW.h`, `J`, `degC`, `degF`, `K`, `mm^2`, `m`, `s`, `ft`, `mi`, `mi/h`, `nmi` (nautical mile), `km`, `L`, `m^3`, `atm`, `kPa`, `bar`, `Pa`, `cal_th` (thermochemical calorie), `in^2`, `min`, `h`, `V`, `mV`, `A`, `W`, `ohm`, `m^2`. `degC` and `degF` in a `convert` task mean a temperature, not a temperature interval. Each adapter translates these spellings into the spelling its tool expects.

## Checking a file

```
python3 tools/check_pairs.py            # format check
python3 -m unittest discover -s tests   # format check, plus every answer recomputed
```

Both use only the Python standard library. They were run with Python 3.13; older versions have not been tried.

## Sources used so far, and their reuse terms

- **NIST Special Publication 811** (2008 edition) and **NIST Technical Note 1297** (1994 edition), read on nist.gov. NIST's [copyright page](https://www.nist.gov/copyrights-disclaimers), read on 24 November 2026, says that information on NIST sites, unless marked as copyrighted, may be distributed or copied, and asks for credit. We take only factors, formulas and their locations, and we credit NIST in every pair.
- **ISO 31-0:1992** (withdrawn, replaced by ISO 80000-1) is under ISO copyright. It is cited by clause number only, with a link to the free sample that shows the clause. Nothing is quoted.
- **Fourier, The Analytical Theory of Heat** (Freeman's translation, 1878) is in the public domain.
- **JCGM documents (GUM, VIM)** are not copied. When a pair cites them, it gives only the document and clause or example number. No pair cites them yet.
