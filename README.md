# Measure

*Русская версия: [README.ru.md](README.ru.md)*

**Status: in progress. The data format ([FORMAT.md](FORMAT.md)) and the first 11 reference pairs ([pairs/pairs.json](pairs/pairs.json)) exist; no tool has been tested yet. The plan is in [PLAN.md](PLAN.md).** Under the [slovo-lab manifesto](https://github.com/slovo-lab/manifesto), a project starts with a written statement, and this is it. Written by Claude (AI), curated by Anton Krugovov.

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
