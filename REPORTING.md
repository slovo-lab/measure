# Reporting what the bench finds

*Русская версия: [REPORTING.ru.md](REPORTING.ru.md)*

**The rule, set by the lab's owner on 25 November 2026: every error the bench finds in a tool is reported to the tool's authors.** There is no choosing whom to tell: a small server and a well-known library are treated alike. Written by Claude (AI).

## What counts as an error

A wrong answer is reported only after all of these are done, and the report file says that they were:

1. **Reproduced without the bench.** The tool is called directly, in a few lines anyone can run. A wrong number that appears only through an adapter is the adapter's error until shown otherwise.
2. **The tool's own documentation read**, including the tutorial and the text that ships inside the package, not only a "known issues" page. If the behaviour is described there as a limit, it is **not reported**. It still stands in the results, with a note that the authors document it, because an agent that calls the tool gets that number.
3. **Existing issues searched.** If someone has reported it, nothing new is opened; the existing issue is linked in the results.
4. **The reference answer has a read source**, quoted in the report.

Not reported one by one: a verdict of `incomplete` (see `FORMAT.md`), a task the tool does not offer, a tool that asks for payment or an account.

## How a report is made

- One issue per point, in the project's own tracker, so each can be discussed and closed alone. If the project has no public tracker, the report goes by e-mail to the address in the package's metadata.
- Every report says in its first lines that it comes from Measure, that it is written by an AI, and who the human curator is.
- It contains: the version, a minimal example, what came back, what was expected and the source. It asks for nothing and suggests no particular fix unless one is obvious.
- No second message if there is no answer.

## Who presses the button

Reports are sent from the owner's account. The rule above settles **whether** to report; it does not replace his look at **each text**: every report is shown to him in Russian and sent only after his "yes" to that text, in a session where he is present. Scheduled sessions prepare reports and never send them.

## Where it is recorded

- `reports/YYYY-MM-DD-<tool>.md`: the text, the checks done, the status (prepared, sent with a link, not sent and why).
- `outreach/issues.md`: every issue opened, and what happened to it.
- A finding that turned out to be the bench's own mistake is corrected in the open, in the same place where it was published.

## Why the checks are strict

On 25 November 2026 the bench recorded four failures for the `quantities` package. Three were the adapter's mistake: the package documents its degrees Celsius as a temperature difference. The fourth, a different uncertainty for `q*q` than for `q**2`, is shown as an example and warned about in the package's own tutorial. Neither was sent to anyone, because the documentation was read first. A report that the authors can answer with a link to their own manual costs them time and costs the lab its name.
