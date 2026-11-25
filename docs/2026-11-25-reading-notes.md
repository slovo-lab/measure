# Reading before the first round: notes

*Русская версия: [2026-11-25-reading-notes.ru.md](2026-11-25-reading-notes.ru.md)*

Written by Claude (AI) on 25 November 2026. Three documents were to be read before the round of 1 December. All three were read, as summaries made by the fetch tool from the pages, not as full texts; the third only after the owner approved the request. Formulas below are as the summary gave them; one of them was marked there as a reading of a damaged formula. Check against the paper before using any of them.

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

## 3. NIST AI 800-2

Read on 25 November, after the owner approved the request: "Practices for Automated Benchmark Evaluations of Language Models", initial public draft of 30 January 2026, comments closed 31 March 2026 (http://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf). Read as a summary made by the fetch tool, not as the full text. The document carries no statement on copyright or reuse; nothing is copied from it here.

What it says, in our words. Nine practices in three groups: say what the evaluation is for and choose tests that fit; design, code, run and debug the evaluation; analyse, share and report. For the report it asks for the objective, the version of the test set, how many items of what kind, the exact versions of what was tested, the settings, results per item, the code, and the uncertainty of the results with each source of variation named and the unmeasured ones pointed out. It asks authors to keep what was observed apart from what is inferred, to state limits, and to compare with similar evaluations. Among the usual defects of an evaluation it lists errors in calling tools and test items that cannot be solved.

It is written for evaluations of language models. Measure has no model between the question and the tool, so the parts about model sampling, budgets and "evaluation awareness" do not apply. The parts about reporting do.

What this means for the report of 1 December:

1. **Already there:** the version of the test set (a commit and a checksum in the announcement), the number and kinds of items, exact versions of every tool (the install lines), results per item (`results.json`), the code.
2. **To add to the report:** one sentence saying what the round is for; a section "what these results do and do not show", with observations (this tool gave this answer to this question on this day) kept apart from anything wider; a line on comparable work, or that none was found.
3. **Uncertainty, stated honestly.** The tools are deterministic programs, so there is no sampling to average over. That is an assumption until checked: run every tool twice in the round and say whether the two runs agree answer for answer. The source of variation that is not measured is the choice of questions: 43 pairs are a small, hand-picked sample of what these tools do, and the report must say so in those words.
4. **Our own defects, their list applied to us:** an error in the adapter is not an error of the tool (the verdict "error" and the rule that an adapter never calculates exist for this); a pair with a wrong reference is their "unsolvable item" (section 2 of `ROUNDS.md` covers it).

A second run changes nothing that the announcement fixed (questions, tools, checks), so it can be added without touching the announcement; the report will say that it was added after the announcement and why.
