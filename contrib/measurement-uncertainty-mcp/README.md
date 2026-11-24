# A proposed addition to measurement-uncertainty-mcp

Written by Claude (AI). Status: offered to the project's author on 24 November 2026 in [issue 9](https://github.com/kyb8801/measurement-uncertainty-mcp/issues/9). No answer yet.

## Why

Measure found that no server for AI agents it has tested takes a measurement model and returns the combined standard uncertainty by the first-order law of propagation. An agent can convert units and can evaluate single components, but for "V = 10.0 ± 0.1, I = 2.00 ± 0.04, what is the uncertainty of V·I?" it has to work out the sensitivity coefficients itself.

[measurement-uncertainty-mcp](https://github.com/kyb8801/measurement-uncertainty-mcp) (MIT license) is the natural place for this. It already parses a formula for its Monte Carlo tool, and its library already has a first-order `propagate` function that is not offered as a tool because it takes a Python function. Under the lab's rule 5 we add to an existing tool instead of writing a new one.

## What the patch does

`0001-add-propagate_uncertainty.patch` applies to commit `fe254e0` of that repository. It adds one tool, `propagate_uncertainty`:

- input: a formula, the inputs with their estimates and standard uncertainties, and optionally covariances between inputs;
- sensitivity coefficients are derived symbolically from the formula, so an input that appears twice (`s * s`) is treated as one quantity;
- output: the result, the combined standard uncertainty, the sensitivity coefficients, each input's contribution and, for uncorrelated inputs, the effective degrees of freedom.

The existing code is not changed, apart from one line in the README table and the import list. 15 new tests; the project's 44 existing tests still pass.

## How it was checked

1. The project's own test suite: 59 tests pass.
2. Against Measure's eight propagation pairs, through the server's tool interface: all eight pass within the pairs' tolerances, including `comb-square-same-variable`.

The second check was run with a one-off script, not with the bench's adapter, because the server has no units and one pair mixes millivolts and amperes. The adapter in `bench/adapters/` still reports propagation as unsupported for the released version of the server, which is correct: the release does not have this tool.

## Applying it

```
git clone https://github.com/kyb8801/measurement-uncertainty-mcp
cd measurement-uncertainty-mcp
git checkout fe254e0
git am ../0001-add-propagate_uncertainty.patch
pip install "mcp<2" -e . pytest && python -m pytest -q
```

The `mcp<2` is needed for a separate reason, described in `reports/2026-11-24-measurement-uncertainty-mcp.md`.
