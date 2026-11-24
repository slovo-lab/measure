# Messages to the author of measurement-uncertainty-mcp

Status: **sent on 24 November 2026**, after the lab owner confirmed, as two issues opened from his account: https://github.com/kyb8801/measurement-uncertainty-mcp/issues/8 (the defect) and https://github.com/kyb8801/measurement-uncertainty-mcp/issues/9 (the offer). The existing issues were read first; neither point had been raised. Written by Claude (AI).

## Issue 1 (a defect)

**Title:** A fresh install does not start: `mcp>=1.0.0` now resolves to mcp 2.x

**Text:**

Hello. This report comes from Measure (https://github.com/slovo-lab/measure), an open test bench that checks unit and uncertainty calculators against reference answers with cited sources. It is written by an AI (Claude) and curated by a human, Anton Krugovov.

On 24 November 2026, in a new virtual environment with Python 3.13:

```
git clone https://github.com/kyb8801/measurement-uncertainty-mcp && cd measurement-uncertainty-mcp && git checkout fe254e0
pip install .
measurement-uncertainty-mcp
```

pip installs mcp 2.3.0, and the server stops at import:

```
File ".../measurement_uncertainty_mcp/server.py", line 333, in <module>
    @APP.list_tools()
AttributeError: 'Server' object has no attribute 'list_tools'
```

With `pip install "mcp<2"` (we used 1.30.0) the server starts and works. `pyproject.toml` declares `mcp>=1.0.0` with no upper bound. An upper bound (`mcp>=1.0.0,<2`) would fix new installs until the server is moved to the 2.x interface.

For what it is worth: with mcp 1.30.0 the server passed all 6 of our reference pairs that it has a tool for (Type A, Type B rectangular and triangular, Welch-Satterthwaite). Results: https://github.com/slovo-lab/measure/blob/main/RESULTS.md

## Issue 2 (an offer)

**Title:** Offer: a `propagate_uncertainty` tool (first-order propagation through a formula, with covariances)

**Text:**

Hello. This comes from Measure (https://github.com/slovo-lab/measure), an open test bench for unit and uncertainty calculators, written by an AI (Claude) and curated by a human, Anton Krugovov.

We tested five servers for AI agents and found none that takes a measurement model and returns the combined standard uncertainty by the law of propagation of uncertainty. Yours is the closest: `monte_carlo_propagate` already parses a formula, and `math_kernel.propagate` already does the first-order calculation, but is not a tool because it takes a Python callable.

We wrote a small addition that closes the gap, and would like to offer it as a pull request if you want it:

- one new tool, `propagate_uncertainty(formula, inputs, covariances)`;
- sensitivity coefficients come from symbolic derivatives of the formula, so `s * s` with one measured `s` gives u = 2·s·u(s), not the value for two independent factors;
- covariances between inputs are accepted (GUM 5.2.2);
- it reuses your AST safety gate before the formula reaches sympy;
- existing code is untouched; 15 new tests, and your 44 existing tests still pass;
- through the tool interface it passes all eight propagation pairs in our reference set.

The patch against `fe254e0`, with notes on how it was checked: https://github.com/slovo-lab/measure/tree/main/contrib/measurement-uncertainty-mcp

If you would prefer a different name, a different result shape, or to write it yourself, that is fine too. The code is offered under your MIT license.
