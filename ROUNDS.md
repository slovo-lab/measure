# Rounds

*Русская версия: [ROUNDS.ru.md](ROUNDS.ru.md)*

Written by Claude (AI) on 25 November 2026. Agreed in outline with the lab's owner on 24 November 2026.

Measure publishes its results in dated rounds, once a month. A round is one day on which the same announced questions are put to every tool, installed fresh that day, and one report is written. Between rounds the bench keeps changing; a round does not.

The form is borrowed from proficiency testing, where a provider sends the same items to many laboratories, compares their results with an assigned value and issues a report for the round. The comparison stops there, and section 7 says where.

## 1. When

- The first working day of each month, by the calendar of Madrid.
- The first round is on **1 December 2026**.
- The results of 24 November 2026 (`results/2026-11-24.json`) are kept as **round 0**: the state before there were any rules.

## 2. What is fixed in advance

At least three working days before a round, an announcement is published in `rounds/<year>-<month>/announcement.md`. It names:

- **the questions**: the reference pairs as they stand in `pairs/pairs.json` at one named commit. Pairs added after that commit wait for the next round;
- **the tools**: every tool that will be asked, by name and by where it will be installed from;
- **the kinds of check** that will be run, if more than the pairs.

A pair found to be wrong after the announcement is not quietly repaired. It is withdrawn from the round, and the report says which pair and why.

## 3. What happens on the day

1. **A fresh install of every tool**, into an empty environment, of the newest released version the package index offers that day. Nothing is pinned to an older version to make a tool work. A tool installed from its repository is taken at the newest commit of its main branch, after the changes since the last round have been read.
2. **One line per tool before any question is asked**: did it install, did it start, which versions of the tool and of its main dependencies were resolved.
3. A tool that does not install or does not start is reported as exactly that. If a workaround is known (for example an older version of a dependency), the tool is then also run with the workaround, and those results are shown apart and labelled, never merged into the first line.
4. **The questions are put through the runner**, as on any other day. The verdicts are the ones in `FORMAT.md`: pass, fail, not offered, error. The tolerances are the ones in the pairs.
5. Reference answers never come from a tool under test. They were fixed in the announcement.

## 4. The report

Each round leaves, in `rounds/<year>-<month>/`:

- `announcement.md`, as published before the round;
- `results.json`, the raw output;
- `report.md` and `report.ru.md`: the install-and-start lines, the table, every failure with what was asked, what was expected and what came back, what was not asked and why, and what changed since the previous round.

The report is also published on the lab's site in English and Russian.

**No ranking.** Tools offer different things, so counts of passes are not comparable between tools, and no overall score or place is given. "Not offered" is not a failure.

**No certificate.** A round says what these tools answered to these questions on this day. It does not say a tool is correct, safe or approved, and it must not be quoted as if it did.

## 5. Earlier rounds are not rewritten

A published round is not edited. If a mistake is found later, in a reference answer, in an adapter or in the report, a dated note is added at the end of that round's report saying what was wrong and what the result should have been, and the next round carries the correction. Mistakes of the bench are reported in the same detail as mistakes of the tools.

## 6. The authors of the tools

- Authors are **not told individually** before a round. The calendar and the announcement are public, and a round is meant to show what an ordinary user would get that day. (Proposed by the AI; the owner has not objected. If he decides otherwise, this point changes.)
- The rule for reports is in [`REPORTING.md`](REPORTING.md): every confirmed error is reported, whenever it is found.
- After a round, a finding with a clear right answer is reported to the tool's authors where they take reports. Every such message is read by the lab's owner before it is sent, says that it was written by an AI, and asks for nothing.
- An author who disagrees with a result can say so in an issue in this repository. The objection is linked from the round's report, with our answer. If the author is right, section 5 applies.
- A tool is in a round because it is published for anyone to install. An author may ask for a statement to be added next to their tool's results; it will be added as written.

## 7. What a round is not

- It is not proficiency testing in the sense of ISO/IEC 17043. Nobody enrolled, nothing is confidential, and the lab is not an accredited provider and does not claim to meet that standard. Only the form is borrowed: announced items, one day, one report, rounds kept.
- It is not a benchmark of language models. No model stands between the question and the tool.
- It is not complete. The pairs cover a small part of what these tools do; the report says which part.

## 8. Who runs it

The round is run by Claude, an AI, in a scheduled session, from this repository. The owner of the lab, Anton Krugovov, reads the report and confirms every message sent outside the lab. Anyone can rerun a round from the announcement: the commit, the tools and the commands are all in it.
