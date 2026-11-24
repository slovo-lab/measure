# A trial: money questions for servers for AI agents

*Русская версия: [README.ru.md](README.ru.md)*

Written by Claude (AI) on 24 November 2026. This folder is a one-day trial, not part of the bench. It was run to answer one question before deciding whether money calculations deserve a reference set of their own: **do finance servers for AI agents disagree with reference answers at all?**

## What was done

Fourteen questions were put to four servers through their tools, the way an agent calls them. Every reference answer is computed in `trial.py` with 40-digit arithmetic from the defining equation; none comes from a server.

One question comes from an official source: example 1 of the European Commission's "Examples for the calculation of the annual percentage rate of charge" (January 2015): 200 000 at 6% nominal, 240 monthly instalments, instalment 1 432.86, costs of 4 000 at signing, rate 6.434412%. Our own calculation gives an instalment of 1 432.862... and, with the instalment rounded to 1 432.86 as in the document, a rate of 6.434412%, the same to all six decimals. The document carries a disclaimer that it is not the Commission's official position; only its numbers are used here, with the source named.

Servers and versions: mcp-finance 0.6.1, vibe-math-mcp 2.0.3, pyxirr-mcp-server 0.2.0, axiom-calculator-mcp 1.0.0. A fifth, personal-finance-mcp 2.0.0, was installed, but its answers are formatted text, and it was only checked by eye.

## What came out

Full table: [results-2026-11-24.md](results-2026-11-24.md). Of 41 answers, 33 agree with the reference, 3 are correct refusals or a correct "there are two answers", and 5 are listed below.

**On ordinary questions every server agrees with the reference.** Loan payments, future value, net present value, a simple rate of return, the rate behind the Commission's example: all four servers that have a tool for the question give the reference value.

**The differences are at the edges.**

1. **A question with two right answers.** The cash flows -1 000, +2 300, -1 320 have two internal rates of return, 10% and 20%. mcp-finance returns both and says the answer is not unique. vibe-math-mcp returns 10% and pyxirr-mcp-server returns 20%, each with no warning. An agent asking two tools the same question gets two different numbers and no hint why.
2. **A question with no answer.** The flows +100, +200, +300 have no rate of return. mcp-finance and pyxirr-mcp-server report an error. vibe-math-mcp returns `NaN` as a successful result.
3. **A very small rate.** For a rate of 1e-12 per period, vibe-math-mcp and pyxirr-mcp-server give a payment of 99.9911 where the reference is 100.00000000065: four correct digits. This does not matter at any rate found in practice (at a realistic small rate the loss is far below a cent); it is noted as a numerical property, not as a defect that could hurt anyone.

**Starting at all.** Two of the five servers, pyxirr-mcp-server 0.2.0 and personal-finance-mcp 2.0.0, did not start after a fresh install on 24 November 2026: they import an interface that the current major version of the `mcp` package no longer has. Both start with `mcp<2`. The same defect was found the same day in a server of another kind (see `reports/2026-11-24-measurement-uncertainty-mcp.md`).

**A convention, not an error.** Three servers report the total paid on the example loan as 343 886.91, which is 240 times the unrounded instalment. A lender collects whole cents, so a real schedule totals differently. Each server is consistent with itself; a reference set would have to say which total it means.

## What this means for the idea

The trial was meant to be able to fail, and on the main question it came close to failing: these servers are numerically sound on the questions people actually ask. A reference set made only of ordinary questions would show a table of passes.

What it did find is narrower: how tools behave when a question has no answer or more than one, and whether they start. These are worth reporting to the authors. They are not, yet, a case for a project of the size of Measure.

Reports to authors: drafts for personal-finance-mcp and vibe-math-mcp are in `reports/`. pyxirr-mcp-server has no public place for reports (its repository address on the package index leads to a private page), so nothing can be sent there.

## Running it

```
python3 -m venv fin-envs/mcp-finance && fin-envs/mcp-finance/bin/pip install mcp-finance==0.6.1
# the same for vibe-math-mcp==2.0.3, pyxirr-mcp-server==0.2.0 (then also "mcp<2"), axiom-calculator-mcp==1.0.0
pip install mcp mpmath
python3 pilots/money/trial.py
```
