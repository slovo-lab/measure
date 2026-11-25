# Reading before the first round: notes

*Русская версия: [2026-11-25-reading-notes.ru.md](2026-11-25-reading-notes.ru.md)*

Written by Claude (AI) on 25 November 2026. Three documents were to be read before the round of 1 December. Two were read, as summaries made by the fetch tool from the pages, not as full texts; the third could not be opened. Formulas below are as the summary gave them; one of them was marked there as a reading of a damaged formula. Check against the paper before using any of them.

## 1. Reference data for software validation (the TraCIM work)

Read: A. B. Forbes, I. M. Smith, G. J. P. Kok, "Generation of reference data for software validation", XXI IMEKO World Congress, 2015 (https://imeko.org/publications/wc-2015/IMEKO-WC-2015-TC21-415.pdf). The paper named in the list, Kok and Smith, "Approaches for assigning numerical uncertainty to reference data pairs for software validation" (2015), has no open full text that was found; this one is by the same group, on the same subject, from the same year. A longer account exists: Kok, Harris, Smith, Forbes, "Reference data sets for testing metrology software", Metrologia 53 (2016), not read.

What it says, in our words:

- A reference pair is not exact. Each reference output carries two numbers: its **accuracy** (how far the stored value is from the value computed with many more digits) and its **sensitivity** (how much the output moves when the input is disturbed by a few units of the working precision; a property of the problem, not of any program).
- The test result is not judged by its raw difference from the reference. The difference is first not allowed to be smaller than the reference's own accuracy, and is then divided by the sensitivity times the working precision. The logarithm of that is the **number of decimal digits the tested software loses beyond what a good program would lose** on that problem.
- Reference outputs are computed with extended precision (100 digits in their example), either forwards from the input or backwards from a chosen output.
- The paper does not say where to put a pass mark. It leaves the single figure of merit out of scope.

What this means for Measure:

1. Our pairs have one tolerance per pair (1e-12 for exact answers, 1e-9 for rounded ones) and say nothing about the accuracy of the reference or the sensitivity of the problem. For unit conversion and simple propagation this is harmless: the problems are well conditioned.
2. It will not be harmless in the fields agreed for later. The near-antipodal distance in the coordinates trial and the payment at a tiny rate in the money trial are exactly the cases this paper is about. There, a fixed tolerance either fails good tools or passes bad ones.
3. Proposal for format version 2, to be decided with the other changes: two optional fields per pair, `reference_accuracy` and `sensitivity`, and, where they are present, a reported "digits lost" next to the verdict. The verdicts stay as they are.
4. Our habit of recomputing every reference with exact fractions or 40 digits is the same idea as their extended precision. It should be said in `FORMAT.md` in those terms, with this paper cited.
5. Their decision to give no pass mark supports ours to give no ranking.

## 2. Mathmet's Quality Assurance Tools (EURAMET, version 1.0.0)

Read: the page https://euramet.org/european-metrology-networks/mathmet/activities/quality-assurance-tools. Not read: the tool itself, which is a set of interactive PDF files in a ZIP archive.

What the page says: the software tool leads the user through a risk assessment that gives an **integrity level from 1 to 4** (1: for example a prototype for internal use; 4: safety-critical software). The level decides which activities go into a quality plan, over a life cycle of requirements, design and development, verification, validation, release, maintenance. No licence is stated on the page; EURAMET disclaims liability.

What this means for Measure:

1. Measure should say, in its own words, what level of care it claims and what was done at each stage. A first, honest account: requirements are in `README.md` and `FORMAT.md`; verification is the test suite that recomputes every answer; validation is thin (no outside reviewer has checked the pairs); release was done once; maintenance is the scheduled sessions and the rounds.
2. The weak point this shows is validation by someone else. That is the review the lab's owner was asked for, and what a metrologist from the outreach list could give.
3. To do: open the tool itself and fill it in for Measure. Not done today.

## 3. NIST AI 800-2 (not read)

"Practices for Automated Benchmark Evaluations of Language Models", initial public draft of 30 January 2026, comments closed 31 March 2026 (https://www.nist.gov/node/1905466; full text http://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf). Known from its page only: three parts (objectives and choice of benchmarks; implementing and running; analysing and reporting) and a glossary; it covers language models and agent systems.

The full text could not be opened on 25 November: the request needed a permission that was not answered. It is the most relevant of the three for how a round's report is written, and it is still to be read before 1 December.
