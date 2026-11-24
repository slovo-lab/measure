# Measure

*Русская версия: [README.ru.md](README.ru.md)*

**Status: first release, version 0.1.0, 24 November 2026. Version 0.1.0 has 33 reference pairs and two tools tested; 10 more pairs were added the same day, so the main branch has 43. The results are in [RESULTS.md](RESULTS.md) and the plan for what comes next is in [PLAN.md](PLAN.md).** Under the [slovo-lab manifesto](https://github.com/slovo-lab/manifesto), a project starts with a written statement, and this is it. Written by Claude (AI), curated by Anton Krugovov.

## In plain words

**Measure is a calibration check for the calculators that AI agents use.**

Language models are poor at arithmetic with units of measurement and uncertainties. So they are given calculator programs to call: "convert miles to kilometres", "what is the uncertainty of this product". Many such programs exist. Nobody outside checks whether the programs themselves give right answers.

Measure does that, in the way an instrument is checked in a laboratory:

1. **A reference.** A set of questions with answers known in advance. Every answer names its source, mostly NIST publications, and is recomputed with exact fractions. There are 43 questions now.
2. **A test.** The same questions are put to each calculator.
3. **A report.** A public table shows where an answer matched the reference, where it differed and by how much, and what the calculator cannot do at all.

Measure calculates nothing new. It only compares other tools' answers with the reference.

**What it has found.** On the first day, two defects in the ucon library: a wrong uncertainty for a number multiplied by itself, and a unit name read in two different ways depending on the target unit. Both were reported to the authors.

**Who it is for.** People choosing a calculator for their agent; authors of calculators, who get a free independent check; and agents themselves, which can read the table to decide which tool to trust.

## Results so far

| Tool | How it was called | Pairs it has a function for | Passed |
|---|---|---|---|
| Pint 0.26.2 + uncertainties 3.2.3 | Python library | 32 | 32 |
| ucon 2.4.2 | Python library | 28 | 27 |
| GTC 1.5.1 (GUM Tree Calculator) | Python library | 13 | 13 |
| ucon-mcp (ucon-tools 0.13.0) | server for AI agents | 18 | 18 |
| unit-converter-mcp 0.1.2 | server for AI agents | 18 | 18 |
| mcp-units 0.1.0 (commit 913fee9) | server for AI agents | 20 | 20 |
| mcp-gnu-units 0.1.1 | server for AI agents | 20 | 20 |
| measurement-uncertainty-mcp 0.1.0 (commit fe254e0) | server for AI agents | 6 | 6 |

There are 43 pairs in all. A tool is only asked the pairs it has a function for; the rest are listed as "not offered" and are not failures. Servers were started locally and called through their tools, the way an agent calls them.

This is how the tools answered on one date. It is not a ranking and not a certificate. The one answer that differed, and the other observations, are explained in [RESULTS.md](RESULTS.md).

No server found so far takes a measurement model and returns the combined uncertainty by the first-order law. That is the category where the one failure was found, and it can only be tested on the Python libraries for now.

## What changed on day one

Measure was first planned as a calculator for AI agents that handles units of measurement and uncertainties. A search on 24 November 2026 found tools that describe themselves as doing that already:

| Tool | What it says it does |
|---|---|
| [ucon](https://pypi.org/project/ucon/) | Units library with uncertainty propagation and a server for AI agents |
| [measurement-uncertainty-mcp](https://github.com/kyb8801/measurement-uncertainty-mcp) | Uncertainty analysis following the GUM, for AI agents |
| [mcp-units](https://github.com/quantumleeps/mcp-units) | Unit conversion for AI agents, based on Pint |
| mcp-gnu-units | Unit conversion for AI agents, based on the GNU units database |

Manifesto rule 5 says not to build duplicates, so that plan is dropped.

## The idea now

An independent test bench for these tools. In metrology an instrument is trusted because it has been compared with a reference. Measure would do the same for calculators that AI agents rely on:

1. A public set of worked examples with known answers, each with its source (for example, the worked examples in the GUM).
2. A runner that puts the same examples to each tool.
3. A published table of results: where each tool agrees with the reference, where it differs, and by how much.

It calculates nothing new. It checks the calculators that exist.

## Why we decided to go ahead

A second round of research on 24 November 2026 answered the open questions well enough to start.

- **The method is established metrology.** Validating software with reference data sets and reference results ("reference pairs") is the approach of the European TraCIM project, which applies the calibration principle to software. Measure borrows that method. It does not invent one.
- **Nobody seems to apply it to tools made for AI agents.** TraCIM certifies specific numerical algorithms as a service. We found no public, cross-tool check of the unit and uncertainty calculators that agents call. This is still "not found", not "does not exist".
- **Reference examples need care.** The GUM documents are under JCGM copyright and may be reproduced only with written permission. So Measure will not copy their text. It starts from cases with exact answers (SI definitions, closed-form formulas) and from NIST publications, and cites GUM examples by number.

## Running it

```
python3 -m unittest discover -s tests        # checks the pairs and the runner
pip install -r requirements-adapters.txt     # the tools under test
python3 -m bench pint                        # puts every pair to Pint + uncertainties
python3 -m bench ucon                        # the same for ucon
python3 -m bench gtc                         # GTC, the GUM Tree Calculator
python3 -m bench ucon-mcp                    # ucon's server for AI agents
python3 -m bench unit-converter-mcp          # another server for AI agents
python3 -m bench mcp-units                   # likewise; also mcp-gnu-units, measurement-uncertainty-mcp
python3 tools/make_results.py                # runs both and rewrites RESULTS.md
```

The runner gives each pair one of four verdicts: `pass`, `fail`, `unsupported` (the tool has no function for that kind of task, which is not a failure) or `error`. An adapter only passes the question to the tool; it never does the calculation itself.

## Who it is for

- People choosing a units or uncertainty tool for an AI agent.
- Authors of those tools, who get a free independent check and reproducible bug reports.
- AI agents, which can read the results table to decide which tool to call.

## Open questions before any code

- Does a cross-tool check like this exist already? A few searches found none, which is not proof.
- Which reference examples can be reused under their licenses?
- Does the idea hold up for a metrologist? (Question for the curator.)

## How we will know it failed

The default from the manifesto applies: if eight weeks after the first release nobody outside the lab uses the results (no tool author responds, no outside issue, no citation), the project is archived with a written account.

## License

Code will be under the MIT license. Text and test data: CC BY 4.0, unless a source requires otherwise.
