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

## Calendar

Work that belongs to a date. On that date it comes before the steps below; on any other day, skip it and take the first unchecked step.

- [ ] **On Tuesday 1 December 2026: run the round.** Read the changes in the two repository-installed servers since `913fee9` and `fe254e0`, run `tools/round.py` as the announcement says, put `results.json` and `install.json` in `rounds/2026-12/`, write `report.md` and `report.ru.md` (section 4 of `ROUNDS.md`), publish the report on the site in both languages.
  The report also follows `docs/2026-11-25-reading-notes.md`, section 3: one sentence on what the round is for; a section on what the results do and do not show; a line on comparable work; and a second run of every tool, with a statement of whether the two runs agree answer for answer (say in the report that the second run was added after the announcement, and why).
- Every later round: publish the announcement at least three working days before the first working day of the month (for January 2027: the round is on Monday 4 January, because 1 January is a public holiday; the announcement is due by Tuesday 29 December 2026).

## Steps

- [x] Define the data format for reference pairs and write the first 10 pairs with sources. Done 24 November 2026: `FORMAT.md`, `pairs/pairs.json`, `tools/check_pairs.py`, `tests/test_pairs.py`. An 11th pair, for dimensional safety, was added the same day. Not covered yet: degrees of freedom, reporting.
- [x] Write the runner and the Pint + uncertainties adapter; add tests for the runner itself. Done 24 November 2026: `bench/` (runner, model evaluator, adapter, command line) and `tests/test_runner.py`. Pint and `uncertainties` have no function for Type A or Type B evaluations, so those pairs come back as `unsupported` for this tool.
- [x] Add the ucon adapter. Done 24 November 2026: `bench/adapters/ucon_adapter.py`, for ucon 2.4.2 used as a Python library. Type A, Type B and inputs with a covariance come back as `unsupported`: we found no function for them in that version.
- [x] Reach 30 pairs; publish the first results table. Done 24 November 2026: 33 pairs, `tools/make_results.py`, `RESULTS.md`, version 0.1.0.
- [x] Tell the authors of the tested tools, by opening an issue in their repositories. This is posting on an outside platform, so it needs the curator's confirmation first. Draft for ucon: `reports/2026-11-24-ucon.md`. Sent 24 November 2026 as ucon issues 395 and 396. Pint and uncertainties had nothing to report. If the authors answer, record the answer in `RESULTS` notes and rerun when a fixed version is out.
- [x] Add pairs for the two empty categories: degrees of freedom and reporting. Each needs a source that has been read first. Done 24 November 2026, after the 0.1.0 tag: 10 new pairs (43 in all). Degrees of freedom: NIST TN 1297, Appendix B.3, equation (B-1). Rounding: NIST SP 811, Appendix B.7.1. Also added: two temperature differences, a conversion that must be refused, two Type B pairs for a normal distribution. Neither tested library offers the new kinds of task, so these pairs wait for the tools that do (the agent-facing uncertainty server).
- [x] Run the tests automatically on every change. Added 24 November 2026: `.github/workflows/tests.yml`, two jobs (reference pairs with plain Python; all adapters with the tools installed).
- [x] Add adapters for tools that run as servers for AI agents. First two done 24 November 2026: `ucon-mcp` (from ucon-tools 0.13.0) and `unit-converter-mcp` 0.1.2, both started as local servers and called through `bench/mcp_client.py`. Both passed all 18 conversion pairs they have a tool for.
- [x] measurement-uncertainty-mcp added on 24 November 2026 (installed from its repository at commit fe254e0, with the owner's approval; it needs no account when run locally). It passed all 6 pairs it has a tool for.
- [x] mcp-units (repository commit 913fee9, approved by the owner) and mcp-gnu-units 0.1.1 (package index, in an environment of its own) added on 24 November 2026. Each passed all 20 conversion pairs.
- [x] Open question answered on 24 November 2026: three more searches found no server that propagates uncertainty through a model to first order. Instead of writing one, an addition to measurement-uncertainty-mcp was prepared: `contrib/measurement-uncertainty-mcp` (a patch with 15 tests; passes all eight propagation pairs).
- [x] Offered the addition to the author of measurement-uncertainty-mcp (issue 9 there) and reported the fresh-install defect (issue 8), 24 November 2026.
- [x] Search for what exists before building the new kinds of check and the kit for authors. Done 24 November 2026, evening: [`docs/2026-11-24-new-checks-prior-art.md`](docs/2026-11-24-new-checks-prior-art.md). Result: no kit and no audit of our own (both exist); kinds 1, 3 and 4 go into the format; kind 2 goes into the rules of a round.
- [x] Add an adapter for the GUM Tree Calculator. Done 24 November 2026, evening: `bench/adapters/gtc_adapter.py`, GTC 1.5.1 from the package index. 13 of 13 pairs it has a function for; 105 tests. It has no units, so the rule for such a tool is now written down in the adapter: a propagation pair is sent only when its numbers can be handed over as they stand.
- [x] Write the rules of a monthly round. Done 25 November 2026: [`ROUNDS.md`](ROUNDS.md) with a Russian version. The standard for proficiency testing is sold, not free to read, so only the generally known shape of a round was used and the rules say plainly that this is not proficiency testing in that sense.
- [x] Publish the announcement for the round of 1 December 2026, and prepare the script for the day. Done 25 November 2026: [`rounds/2026-12/announcement.md`](rounds/2026-12/announcement.md) with a Russian version (the commit of the pairs, the eight tools and where each comes from, the commands), and `tools/round.py` with `tests/test_round.py`. The script was tried once on all eight tools: seven installed and started; measurement-uncertainty-mcp installed and did not start (pip resolved mcp 2.3.0), then started in a second environment with `mcp<2`; the answers were the same as on 24 November. Decided on the way: one empty environment per tool, and one client with a fixed `mcp` version for all servers, as the bench's own equipment.
- [x] Propose format version 2. Done 25 November 2026: a section in [`FORMAT.md`](FORMAT.md), the checker (`tools/check_pairs.py` accepts versions 1 and 2), four examples in `pairs/proposed-v2.json`, 16 new tests. Besides the three kinds of pair it adds a verdict `incomplete` and two optional fields on how good a reference is, after the 2015 paper of the TraCIM group. The published pairs stay at version 1.
- [x] Teach the runner version 2. Done 25 November 2026: `bench/runner.py` judges `any_of`, `must_state` and relations (one call feeding the next), with the verdict `incomplete`; an adapter is shown the question only, never the answers; 19 new tests. The Pint and ucon adapters report what their tool states. Version 1 pairs give the same reports as before (same counts, same four keys; the existing tests and a new one prove it), so the round of 1 December is not affected. First trial: [`docs/2026-11-25-v2-first-run.md`](docs/2026-11-25-v2-first-run.md).
- [ ] Let the other adapters report what their tool states (the five servers answer in text or JSON that carries the unit; GTC has no units). Then decide, with the owner's answers to the open questions in `FORMAT.md`, which examples move into `pairs/pairs.json`, and raise its version. Not before the round of 1 December is run.
- [ ] Coordinates: read the Australian manual and a definition of UTM zones (including the Norway exception) in full, check their reuse terms, then write the first pairs for lengths, areas and conversions.
- [ ] Read the documentation of `mcp-assert` and the suites repository linked from `mcp-test-harness`; decide whether and how to give Measure's pairs in a form such a framework can run. Look for a numeric tolerance and for "must refuse".
- [ ] When a released server has first-order propagation, add the task to its adapter. The server has no units, so decide first how pairs that mix units are put to it.

## Every session

Not a step that can be ticked: read the outside issues and record what is there in [`outreach/issues.md`](outreach/issues.md) (fourteen issues as of 24 November 2026). If the author of measurement-uncertainty-mcp accepts the offer in issue 9, a pull request needs a fork of his repository in the slovo-lab organization, which the owner has to create or approve. If an author publishes a fix, rerun and record it in the results notes. This was a checkbox until 24 November 2026; it was moved here because a step that is never finished hid the steps after it.

## Open points

- **Dimensional safety: source found on 24 November 2026.** ISO 31-0:1992, clause 2.2.1 states the rule; the clause is in the free sample of the standard. The standard is withdrawn and replaced by ISO 80000-1, whose text we have not read; its clause number should replace this one when someone with access checks it. Fourier, Analytical Theory of Heat (1878 translation), Art. 160 is cited as a public-domain second source. The first pair, `dim-add-length-time`, uses both. Later the same day a current source was added to every such pair: ISO/IEC Directives, Part 2 (ninth edition, 2021), Annex B, which is free to read and states the same rule. The clause number in ISO 80000-1 is therefore no longer needed; that standard is paid and its text has still not been read.
- **Candidate pair: a quantity minus itself.** `x - x` is exactly zero with zero uncertainty, because x is fully correlated with itself. A tool that treats the two operands as independent reports a non-zero uncertainty. Needs a source and a decision on how to put the question fairly to tools that do not track correlation.
- **GUM cross-references.** The first pairs cite NIST Technical Note 1297, which is free to read. Matching GUM clause numbers can be added once each has been checked against the document.

## Rules for fairness

- A failed case is reported to the tool's authors before or together with publication, with steps to reproduce it.
- The table states what was tested and what was not. A tool is never called "wrong" in general on the basis of a few cases.
- If a reference answer turns out to be wrong, the correction is published and dated.
