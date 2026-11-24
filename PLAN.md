# Measure: plan

Written by Claude (AI) on 24 November 2026. This file is the working plan; update it as steps are finished.

## First release: what it contains

1. **Reference pairs**, 30 to 50 of them, in a plain data file. Each pair has: an id, the question in words, the inputs with units, the reference answer with its tolerance, and the source of the reference answer.
2. **A runner** that puts every pair to each tool under test and records the answer, the difference from the reference, and pass or fail.
3. **Adapters** for two tools to begin with: Pint with the `uncertainties` package (as a widely used baseline) and ucon.
4. **A results table** published in the repository and on the blog, with the exact tool versions and the date.

## Where reference answers come from

- Exact SI definitions and exact conversion factors (for example, 1 inch = 25.4 mm exactly).
- Formulas with closed-form answers for uncertainty propagation (sums, products, powers, correlated inputs).
- NIST publications: Technical Note 1900 examples, Special Publication 811 conversion factors, results from the NIST Uncertainty Machine. Check the reuse terms of each before copying anything.
- GUM examples: cited by document and example number only. No text is copied, because JCGM publications require written permission to reproduce.

Every reference answer must be derivable by a reader from the stated source. No answer is taken from a tool under test.

## Categories of pairs

- Unit conversion, including offset units (temperature) and compound units.
- Dimensional safety: cases that must be refused (adding metres to seconds).
- Type A evaluation from repeated readings.
- Type B evaluation from stated limits and distributions.
- Combined and expanded uncertainty, with and without correlation.
- Effective degrees of freedom (Welch-Satterthwaite).
- Reporting: rounding of the uncertainty and the result.

## Steps

- [x] Define the data format for reference pairs and write the first 10 pairs with sources. Done 24 November 2026: `FORMAT.md`, `pairs/pairs.json`, `tools/check_pairs.py`, `tests/test_pairs.py`. An 11th pair, for dimensional safety, was added the same day. Not covered yet: degrees of freedom, reporting.
- [x] Write the runner and the Pint + uncertainties adapter; add tests for the runner itself. Done 24 November 2026: `bench/` (runner, model evaluator, adapter, command line) and `tests/test_runner.py`. Pint and `uncertainties` have no function for Type A or Type B evaluations, so those pairs come back as `unsupported` for this tool.
- [x] Add the ucon adapter. Done 24 November 2026: `bench/adapters/ucon_adapter.py`, for ucon 2.4.2 used as a Python library. Type A, Type B and inputs with a covariance come back as `unsupported`: we found no function for them in that version.
- [x] Reach 30 pairs; publish the first results table. Done 24 November 2026: 33 pairs, `tools/make_results.py`, `RESULTS.md`, version 0.1.0.
- [x] Tell the authors of the tested tools, by opening an issue in their repositories. This is posting on an outside platform, so it needs the curator's confirmation first. Draft for ucon: `reports/2026-11-24-ucon.md`. Sent 24 November 2026 as ucon issues 395 and 396. Pint and uncertainties had nothing to report. If the authors answer, record the answer in `RESULTS` notes and rerun when a fixed version is out.
- [x] Add pairs for the two empty categories: degrees of freedom and reporting. Each needs a source that has been read first. Done 24 November 2026, after the 0.1.0 tag: 10 new pairs (43 in all). Degrees of freedom: NIST TN 1297, Appendix B.3, equation (B-1). Rounding: NIST SP 811, Appendix B.7.1. Also added: two temperature differences, a conversion that must be refused, two Type B pairs for a normal distribution. Neither tested library offers the new kinds of task, so these pairs wait for the tools that do (the agent-facing uncertainty server).
- [ ] Run the tests automatically on every change (a GitHub Actions workflow). Not set up yet; tests are run by hand.
- [ ] Add adapters for tools that run as servers for AI agents (measurement-uncertainty-mcp, mcp-units, mcp-gnu-units).

## Open points

- **Dimensional safety: source found on 24 November 2026.** ISO 31-0:1992, clause 2.2.1 states the rule; the clause is in the free sample of the standard. The standard is withdrawn and replaced by ISO 80000-1, whose text we have not read; its clause number should replace this one when someone with access checks it. Fourier, Analytical Theory of Heat (1878 translation), Art. 160 is cited as a public-domain second source. The first pair, `dim-add-length-time`, uses both.
- **Candidate pair: a quantity minus itself.** `x - x` is exactly zero with zero uncertainty, because x is fully correlated with itself. A tool that treats the two operands as independent reports a non-zero uncertainty. Needs a source and a decision on how to put the question fairly to tools that do not track correlation.
- **GUM cross-references.** The first pairs cite NIST Technical Note 1297, which is free to read. Matching GUM clause numbers can be added once each has been checked against the document.

## Rules for fairness

- A failed case is reported to the tool's authors before or together with publication, with steps to reproduce it.
- The table states what was tested and what was not. A tool is never called "wrong" in general on the basis of a few cases.
- If a reference answer turns out to be wrong, the correction is published and dated.
