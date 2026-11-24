# Draft report for vibe-math-mcp: IRR returns NaN as a successful result

Status: draft, not sent. Sending needs the lab owner's confirmation. Written by Claude (AI).
Where: https://github.com/apetta/vibe-math-mcp/issues (no issues at all there on 24 November 2026).

**Title:** `financial_calcs` IRR: NaN returned as a successful result; one of two valid rates returned without a note

**Body:**

Hello. Two observations on `financial_calcs` with `calculation: "irr"` in vibe-math-mcp 2.0.3, both at the edges; on ordinary questions the tool agreed with our reference values to 14 digits or better.

1. Cash flows with no sign change have no internal rate of return. The call

   ```
   {"calculation": "irr", "cash_flows": [100, 200, 300]}
   ```

   returns a normal, successful result with `"result": NaN`. An agent reading this gets no error to react to, and `NaN` is also not valid JSON for strict parsers. An error saying that the cash flows need at least one sign change would be clearer.

2. Cash flows with two sign changes can have two valid rates. The call

   ```
   {"calculation": "irr", "cash_flows": [-1000, 2300, -1320]}
   ```

   returns 0.1. Both 0.1 and 0.2 make the net present value zero. This is a property of the underlying routine, not a wrong number, but the answer carries no hint that it is not unique. A short note in the result when the flows change sign more than once would let an agent know.

Neither is urgent. They are offered as observations.

About this report: it was written by an AI (Claude), working for the open project slovo-lab, and is posted from the account of the project's owner, who read it first. The questions, reference values and results for four servers are here: https://github.com/slovo-lab/measure/tree/main/pilots/money
