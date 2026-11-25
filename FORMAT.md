# Reference pairs: data format

Written by Claude (AI). Format version 1, 24 November 2026. A version 2 is proposed further down (25 November 2026); the published pairs use version 1.

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
| `task` | The kind of calculation: `convert`, `type_a`, `type_b`, `propagate`, `add`, `effective_dof` or `round`. It fixes the shape of `inputs` and the names of the outputs. |
| `inputs` | The same data as in the question, in machine-readable form. See below. |
| `reference` | The expected result. See below. |
| `sources` | One or more sources: `document`, `locator`, optional `url`, and `checked` (the date we read it, `YYYY-MM-DD`). |
| `derivation` | The arithmetic from the source to the answer, in words a reader can follow with a pocket calculator. |

## Tasks

| `task` | `inputs` | Output names |
|---|---|---|
| `convert` | `value`, `unit`, `to_unit` | `value` |
| `type_a` | `readings` (list), `unit` | `mean`, `standard_uncertainty` (of the mean) |
| `type_b` | `distribution` (`rectangular`, `triangular` or `normal`), `half_width`, `unit`; for `normal` also `coverage_probability` (the probability that the value lies within the half-width) | `standard_uncertainty` |
| `effective_dof` | `components` (list of two or more, each with `contribution`, the standard uncertainty already multiplied by its sensitivity coefficient, and `degrees_of_freedom`), `unit` | `effective_degrees_of_freedom` (not rounded or truncated) |
| `round` | `value`, `significant_digits` (a whole number) | `value` |
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
- `tolerance` says how far a tool's answer may be from the reference and still pass: `relative` (a fraction of the reference value) or `absolute` (in the output unit). Almost all tolerances only allow for ordinary double-precision arithmetic: `1e-12` for exact answers and `1e-9` for rounded ones. Two Type B pairs use `1e-4`, because the divisor printed in their source (3, or 1.960) is itself rounded and a tool that uses the exact normal quantile must not fail for that; each such pair says so in its derivation. Tolerances are not a judgment about how much error is acceptable in practice.
- A pair where the correct behaviour is to refuse (for example, adding a length to a time) has `"reference": { "outcome": "refuse" }` and no outputs. A tool passes if it reports an error or declines, and fails if it returns any number. The first such pair, `dim-add-length-time`, was added on 24 November 2026. The pair `dim-add-foot-inch` is the opposite control: a sum of two lengths in different units, which has an answer, so that a tool cannot pass this category by refusing every sum.

## Version 2 (a proposal, 25 November 2026)

The published pairs stay at version 1. Version 2 is proposed here, the checker accepts it, and four examples are in [`pairs/proposed-v2.json`](pairs/proposed-v2.json). The runner understands it since the afternoon of 25 November, and two adapters (Pint, ucon) report what their tool states; the first trial of the four examples is in [`docs/2026-11-25-v2-first-run.md`](docs/2026-11-25-v2-first-run.md). **None of it is in the round of 1 December 2026**, whose questions were announced before. A file says which version it uses in `format_version`; everything in version 1 means the same in version 2.

Version 2 adds three kinds of question and two optional fields. They come from what the lab's trials of 24 November found: tools whose arithmetic is right but which answer a question that has two answers with one, give two different answers to one question, or leave out what the number means. What was searched before proposing them is in [`docs/2026-11-24-new-checks-prior-art.md`](docs/2026-11-24-new-checks-prior-art.md).

### 1. A question with more than one right answer

```json
"reference": { "outcome": "any_of", "refusal_passes": true, "answers": [
  { "reading": "thermochemical calorie", "stated_as": ["thermochemical", "cal_th"],
    "outputs": [ { "name": "value", "value": "4.184", "unit": "J", "exact": true,
                   "tolerance": { "kind": "relative", "value": "1e-12" } } ] },
  { "reading": "International Table calorie", "stated_as": ["international table", "cal_it"],
    "outputs": [ ... ] } ] }
```

- `answers` lists every answer that is right, two or more, each with the `reading` of the question that leads to it and its own `outputs`. Every answer needs a source, like any other.
- `stated_as` lists the words by which a tool may say that it took this reading. They are compared without regard to capitals.
- `refusal_passes` says whether declining, with a request to say which reading is meant, counts as right. It has no default, so that every such pair says it.

What a tool's answer earns:

| The tool | Verdict |
|---|---|
| gives one of the answers and says which reading it took | pass |
| gives all the answers | pass |
| declines, and `refusal_passes` is true | pass |
| gives one of the answers and says nothing about which | **incomplete** |
| gives a number that is none of the answers, or names a reading that does not go with its number | fail |

`incomplete` is a new verdict. It means: the number is right, and something the answer had to say is missing. It is reported apart from pass and from fail and is counted with neither.

A question with *no* right answer needs nothing new: it is a pair whose reference is `"outcome": "refuse"`, as in version 1.

### 2. What an answer must say

```json
"reference": { "outputs": [ ... ],
  "must_state": [ { "what": "unit", "accept": ["mm", "millimetre", "millimeter"] } ] }
```

`must_state` lists what the answer has to carry besides the number. `what` is one of `unit`, `time_zone`, `method`, `datum`, `reading`, `not_unique`. With `accept`, the tool's own words must be one of those listed; without it, saying anything at all for that label is enough.

The adapter reports what the tool said, word for word, and never fills a label in for the tool. An adapter that does not report this at all gets the verdict `unsupported` on such a question, with a note that the gap is in the adapter: a tool is never marked `incomplete` for something the bench did not look at. A label that is missing makes the verdict `incomplete`. A label that is present and wrong (a time in New York marked as UTC) makes it `fail`.

### 3. A relation between a tool's own answers

```json
{ "id": "rel-inch-mm-round-trip", "category": "self-consistency", "kind": "relation",
  "question": "Convert 7 inches to millimetres, then convert the result back to inches. The second result must be 7.",
  "calls": [
    { "name": "there", "task": "convert", "inputs": { "value": "7", "unit": "in", "to_unit": "mm" },
      "outputs": [ { "name": "value", "unit": "mm" } ] },
    { "name": "back", "task": "convert",
      "inputs": { "value": { "from": "there.value" }, "unit": "mm", "to_unit": "in" },
      "outputs": [ { "name": "value", "unit": "in" } ] } ],
  "relation": { "kind": "equal", "left": "back.value", "right": "7",
                "tolerance": { "kind": "relative", "value": "1e-12" } },
  "sources": [ ... ], "derivation": "..." }
```

This is metamorphic testing (T. Y. Chen, S. C. Cheung and S. M. Yiu, 1998): when no reference value is at hand, or to test something a reference value cannot, check a relation that must hold between answers.

- An item with `"kind": "relation"` has `calls` in place of `task`, `inputs` and `reference`. Each call is a task from the table above with its `inputs`, and the `outputs` it is asked for by name and unit, with no values.
- An input may be `{ "from": "there.value" }`: the tool's own output from an earlier call, passed on as the tool gave it.
- `relation` has `kind` (only `equal` so far), a `left` and a `right` side, and a `tolerance`. A side is plain arithmetic over numbers and outputs written as `call.output`. A relative tolerance is taken against the larger of the two sides.
- **Rule 1 becomes: every relation has a source.** The source and the `derivation` must say why the relation holds, in the same detail as for an answer.
- Verdicts: pass if the relation holds; fail if it does not, or if the tool refuses one of the calls; unsupported if the tool lacks a function for any of the calls.

A relation says nothing about which of the answers is right. It says the tool must not disagree with itself.

### 4. How good the reference is (optional fields)

An output may carry two more numbers:

- `reference_accuracy`: a bound on how far the stored reference value is from the true value, in the output's unit. `"0"` for an exact answer.
- `sensitivity`: how strongly the answer reacts to the last digits of the input, 1 or more. 1 for a well-conditioned question.

They follow the way reference data for metrology software is described by A. B. Forbes, I. M. Smith and G. J. P. Kok ("Generation of reference data for software validation", XXI IMEKO World Congress, 2015); see [`docs/2026-11-25-reading-notes.md`](docs/2026-11-25-reading-notes.md). In version 2 they are recorded only. They change no verdict. A reported "digits lost", computed from them as in that paper, is intended, and waits until the paper has been read in full and its formula checked.

### New categories

`ambiguous-input`, `self-consistency`, `labelling`.

### Decided on 25 November 2026: what `incomplete` means for a bare unit name

The lab's owner left this to the AI. Six tools were asked by hand what they take "calorie", "gallon", "pint" and "ton" to mean ([`docs/2026-11-25-more-tools.md`](docs/2026-11-25-more-tools.md)). All six chose the same reading, the one usual in the United States, and none said so in its answer.

1. **The verdict stays `incomplete`.** It describes the answer truthfully: one of the right numbers, and no word about which reading was taken. A convention that every tool shares is still a convention the reader of the answer cannot see.
2. **An `incomplete` is never reported to a tool's authors as a defect on its own.** It is a choice, usually a documented one. In a round it is shown in its own column and summed over tools ("six of six took the US gallon and did not say so"), which is where it tells something.
3. **A question of this kind is published only with a source for each reading**, and preferably where the readings are both in daily use (the gallon, the pint) more than where one is a specialist's distinction (the calorie). The calorie stays as the example in the proposal file.
5. **What counts as declining.** A reply that turns the bare word down and shows the readings the tool does have (a list of accepted names, or "similar units: metric_ton, short_ton") is a decline and passes. A bare "unknown unit" is recorded as the unit not being offered: it does not tell the asker what to choose from. (Added the same day, after two servers answered "ton" in the first way and three libraries in the second.)
6. A tool that names its reading in the answer, or gives both, passes. A tool whose name for the unit is the bare word again ("calorie") has not named its reading.

### What is still open

- Whether giving all the answers should pass when the question, read plainly, asks for one.
- How an adapter reports what a tool stated when the tool's answer is free text.
- No task exists yet for time or for positions; the first pairs in those fields will add them.

## Units

Units are written in plain ASCII: `mm`, `in`, `lb`, `kg`, `km/h`, `m/s`, `kW.h`, `J`, `degC`, `degF`, `K`, `mm^2`, `m`, `s`, `ft`, `mi`, `mi/h`, `nmi` (nautical mile), `km`, `L`, `m^3`, `atm`, `kPa`, `bar`, `Pa`, `cal_th` (thermochemical calorie), `in^2`, `min`, `h`, `V`, `mV`, `A`, `W`, `ohm`, `m^2`, `delta_degF` and `delta_degC` (a temperature difference), `1` (a pure number). `degC` and `degF` mean a temperature, with its offset; `delta_degC` and `delta_degF` mean a difference between two temperatures, with no offset. Each adapter translates these spellings into the spelling its tool expects.

## Checking a file

```
python3 tools/check_pairs.py            # format check
python3 -m unittest discover -s tests   # format check, plus every answer recomputed
```

Both use only the Python standard library. They were run with Python 3.13; older versions have not been tried.

## Sources used so far, and their reuse terms

- **NIST Special Publication 811** (2008 edition) and **NIST Technical Note 1297** (1994 edition), read on nist.gov. NIST's [copyright page](https://www.nist.gov/copyrights-disclaimers), read on 24 November 2026, says that information on NIST sites, unless marked as copyrighted, may be distributed or copied, and asks for credit. We take only factors, formulas and their locations, and we credit NIST in every pair.
- **ISO/IEC Directives, Part 2** (ninth edition, 2021) is free to read on iso.org and is under ISO/IEC copyright. Its Annex B is normative for how ISO and IEC documents treat quantities and units, and it states the rule that only quantities of the same kind can be added or subtracted. It is cited by location only. It is the current source for the dimensional-safety pairs.
- **ISO 31-0:1992** (withdrawn, replaced by ISO 80000-1) is under ISO copyright. It is cited by clause number only, with a link to the free sample that shows the clause. Nothing is quoted.
- **Fourier, The Analytical Theory of Heat** (Freeman's translation, 1878) is in the public domain.
- **JCGM documents (GUM, VIM)** are not copied. When a pair cites them, it gives only the document and clause or example number. No pair cites them yet.
