#!/usr/bin/env python3
"""A one-day trial: put the same money questions to several servers for AI agents.

This is a trial, not part of the bench. It answers one question: do finance
servers for AI agents disagree with reference answers at all?

Each server is installed in a virtual environment of its own under one
directory (default ./fin-envs, or the variable MEASURE_FIN_DIR), for example
fin-envs/mcp-finance/bin/mcp-finance. See README.md in this folder.

Reference answers are computed here with 40-digit arithmetic (mpmath) from the
defining equations, never taken from a server. Written by Claude (AI).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import mpmath as mp  # noqa: E402

from bench.mcp_client import ServerError, StdioServer  # noqa: E402

mp.mp.dps = 40
M = mp.mpf
BASE = os.environ.get("MEASURE_FIN_DIR", os.path.join(os.getcwd(), "fin-envs"))
TOLERANCE = M("1e-9")   # relative; one cent on a payment is checked separately


def pmt(pv, rate, n):
    """Level payment at the end of each period: PV = PMT * (1 - (1+r)^-n) / r."""
    return M(pv) / n if rate == 0 else M(pv) * M(rate) / (1 - (1 + M(rate)) ** -n)


def irr(flows, low, high):
    """The rate r in [low, high] at which sum(flow_k / (1+r)^k) is zero."""
    return mp.findroot(lambda r: sum(M(c) / (1 + r) ** k for k, c in enumerate(flows)),
                       (M(low), M(high)), solver="anderson", tol=1e-35)


PAYMENT = pmt(200000, "0.005", 240)
EXAMPLE_FLOWS = [196000.0] + [-float(PAYMENT)] * 240

# name -> (question in words, reference value or None, kind)
#   kind "number": compare with the reference, sign ignored (servers differ on sign convention)
#   kind "refuse": the right behaviour is an error, because no answer exists
#   kind "two":    two answers are equally valid; the right behaviour is to say so
QUESTIONS = {
    "payment-commission-example-1": (
        "Monthly payment on 200 000 at 6% nominal a year, 240 months "
        "(European Commission, APRC examples, 2015, example 1: 1 432.86)", PAYMENT, "number"),
    "payment-zero-rate": ("Monthly payment on 1 200 at 0%, 12 months", M(100), "number"),
    "payment-negative-rate": ("Payment on 10 000 at -0.1% a period, 12 periods",
                              pmt(10000, "-0.001", 12), "number"),
    "payment-tiny-rate": ("Payment on 1 200 at 1e-12 a period, 12 periods",
                          pmt(1200, "1e-12", 12), "number"),
    "payment-at-start": ("As example 1, payments at the start of each period",
                         PAYMENT / (1 + M("0.005")), "number"),
    "future-value-annual": ("1 000 at 5% a year, compounded yearly, after 10 years",
                            M(1000) * M("1.05") ** 10, "number"),
    "future-value-continuous": ("1 000 at 5% a year, compounded continuously, after 10 years",
                                M(1000) * mp.e ** M("0.5"), "number"),
    "npv": ("Net present value at 10% of -50 000 now, then 15 000, 18 000, 20 000, 22 000",
            sum(M(c) / M("1.1") ** k for k, c in enumerate([-50000, 15000, 18000, 20000, 22000])),
            "number"),
    "irr-simple": ("Internal rate of return of -1 000, then 500 three times",
                   irr([-1000, 500, 500, 500], "0.2", "0.3"), "number"),
    "irr-commission-example-1": (
        "Monthly rate of return of +196 000, then the example-1 payment 240 times "
        "(the monthly rate behind the example's annual percentage rate)",
        irr([196000] + [-PAYMENT] * 240, "0.004", "0.006"), "number"),
    "rate-doubling": ("Rate per period at which 1 000 becomes 2 000 in 10 periods",
                      M(2) ** (M(1) / 10) - 1, "number"),
    "effective-rate": ("Effective annual rate for 12% nominal, compounded monthly",
                       M("1.01") ** 12 - 1, "number"),
    "irr-no-sign-change": ("Internal rate of return of +100, +200, +300 (none exists)",
                           None, "refuse"),
    "irr-two-answers": ("Internal rate of return of -1 000, +2 300, -1 320 "
                        "(both 10% and 20% satisfy the definition)", (M("0.1"), M("0.2")), "two"),
}

# server -> question -> (tool, arguments, key of the number in the answer)
SERVERS = {
    "mcp-finance": {
        "payment-commission-example-1": ("time_value_of_money", {"solve_for": "pmt", "pv": 200000, "rate": 0.005, "nper": 240}, "solved_value"),
        "payment-zero-rate": ("time_value_of_money", {"solve_for": "pmt", "pv": 1200, "rate": 0.0, "nper": 12}, "solved_value"),
        "payment-negative-rate": ("time_value_of_money", {"solve_for": "pmt", "pv": 10000, "rate": -0.001, "nper": 12}, "solved_value"),
        "payment-tiny-rate": ("time_value_of_money", {"solve_for": "pmt", "pv": 1200, "rate": 1e-12, "nper": 12}, "solved_value"),
        "payment-at-start": ("time_value_of_money", {"solve_for": "pmt", "pv": 200000, "rate": 0.005, "nper": 240, "when": "begin"}, "solved_value"),
        "future-value-annual": ("time_value_of_money", {"solve_for": "fv", "pv": -1000, "rate": 0.05, "nper": 10}, "solved_value"),
        "npv": ("npv", {"rate": 0.1, "cashflows": [-50000, 15000, 18000, 20000, 22000]}, "npv"),
        "irr-simple": ("irr", {"cashflows": [-1000, 500, 500, 500]}, "irr"),
        "irr-commission-example-1": ("irr", {"cashflows": EXAMPLE_FLOWS}, "irr"),
        "rate-doubling": ("time_value_of_money", {"solve_for": "rate", "pv": -1000, "fv": 2000, "nper": 10, "pmt": 0}, "solved_value"),
        "effective-rate": ("convert_rate", {"rate": 0.12, "periods_per_year": 12, "direction": "nominal_to_effective"}, "converted_rate"),
        "irr-no-sign-change": ("irr", {"cashflows": [100, 200, 300]}, "irr"),
        "irr-two-answers": ("irr", {"cashflows": [-1000, 2300, -1320]}, "irr"),
    },
    "vibe-math-mcp": {
        "payment-commission-example-1": ("financial_calcs", {"calculation": "pmt", "rate": 0.005, "periods": 240, "present_value": 200000, "future_value": 0}, "result"),
        "payment-zero-rate": ("financial_calcs", {"calculation": "pmt", "rate": 0.0, "periods": 12, "present_value": 1200, "future_value": 0}, "result"),
        "payment-negative-rate": ("financial_calcs", {"calculation": "pmt", "rate": -0.001, "periods": 12, "present_value": 10000, "future_value": 0}, "result"),
        "payment-tiny-rate": ("financial_calcs", {"calculation": "pmt", "rate": 1e-12, "periods": 12, "present_value": 1200, "future_value": 0}, "result"),
        "payment-at-start": ("financial_calcs", {"calculation": "pmt", "rate": 0.005, "periods": 240, "present_value": 200000, "future_value": 0, "when": "begin"}, "result"),
        "future-value-annual": ("compound_interest", {"principal": 1000, "rate": 0.05, "time": 10, "frequency": "annual"}, "result"),
        "future-value-continuous": ("compound_interest", {"principal": 1000, "rate": 0.05, "time": 10, "frequency": "continuous"}, "result"),
        "npv": ("financial_calcs", {"calculation": "npv", "rate": 0.1, "cash_flows": [-50000, 15000, 18000, 20000, 22000]}, "result"),
        "irr-simple": ("financial_calcs", {"calculation": "irr", "cash_flows": [-1000, 500, 500, 500]}, "result"),
        "irr-commission-example-1": ("financial_calcs", {"calculation": "irr", "cash_flows": EXAMPLE_FLOWS}, "result"),
        "rate-doubling": ("financial_calcs", {"calculation": "rate", "periods": 10, "present_value": -1000, "future_value": 2000, "payment": 0}, "result"),
        "irr-no-sign-change": ("financial_calcs", {"calculation": "irr", "cash_flows": [100, 200, 300]}, "result"),
        "irr-two-answers": ("financial_calcs", {"calculation": "irr", "cash_flows": [-1000, 2300, -1320]}, "result"),
    },
    "pyxirr-mcp-server": {
        "payment-commission-example-1": ("pmt", {"rate": 0.005, "nper": 240, "pv": 200000}, "pmt"),
        "payment-zero-rate": ("pmt", {"rate": 0.0, "nper": 12, "pv": 1200}, "pmt"),
        "payment-negative-rate": ("pmt", {"rate": -0.001, "nper": 12, "pv": 10000}, "pmt"),
        "payment-tiny-rate": ("pmt", {"rate": 1e-12, "nper": 12, "pv": 1200}, "pmt"),
        "payment-at-start": ("pmt", {"rate": 0.005, "nper": 240, "pv": 200000, "pmt_at_beginning": True}, "pmt"),
        "future-value-annual": ("fv", {"rate": 0.05, "nper": 10, "pmt": 0, "pv": -1000}, "fv"),
        "npv": ("npv", {"rate": 0.1, "amounts": [-50000, 15000, 18000, 20000, 22000]}, "npv"),
        "irr-simple": ("irr", {"amounts": [-1000, 500, 500, 500]}, "rate"),
        "irr-commission-example-1": ("irr", {"amounts": EXAMPLE_FLOWS}, "rate"),
        "rate-doubling": ("rate", {"nper": 10, "pmt": 0, "pv": -1000, "fv": 2000}, "rate"),
        "irr-no-sign-change": ("irr", {"amounts": [100, 200, 300]}, "rate"),
        "irr-two-answers": ("irr", {"amounts": [-1000, 2300, -1320]}, "rate"),
    },
    "axiom-calculator-mcp": {
        "payment-commission-example-1": ("mortgage_calculator", {"home_price": 200000, "down_payment_pct": 0, "annual_rate_pct": 6, "years": 20}, "monthly_principal_interest"),
        "payment-zero-rate": ("mortgage_calculator", {"home_price": 1200, "down_payment_pct": 0, "annual_rate_pct": 0, "years": 1}, "monthly_principal_interest"),
        "future-value-annual": ("compound_interest", {"principal": 1000, "annual_rate_pct": 5, "years": 10, "compounding_frequency": "annually"}, "final_value"),
    },
}
# Servers that answer in whole cents; for them a difference under half a cent is agreement.
ROUNDS_TO_CENTS = {"axiom-calculator-mcp"}


def as_dict(payload, text):
    """Some servers send their JSON as a string inside {"result": "..."}."""
    if isinstance(payload, dict):
        inner = payload.get("result")
        if set(payload) == {"result"} and isinstance(inner, str):
            try:
                return json.loads(inner)
            except ValueError:
                return None
        return payload
    try:
        return json.loads(payload if isinstance(payload, str) else text)
    except (TypeError, ValueError):
        return None


def judge(server, name, is_error, payload, text):
    words, reference, kind = QUESTIONS[name]
    _tool, _args, key = SERVERS[server][name]
    flat = " ".join(text.split())
    data = as_dict(payload, text)
    value = data.get(key) if isinstance(data, dict) else None
    if kind == "refuse":
        if is_error:
            return "refused (right)", flat[:70]
        if isinstance(value, float) and value != value:
            return "returned NaN as a successful answer", ""
        return "answered %r where no answer exists" % (value,), ""
    if is_error or not isinstance(value, (int, float)):
        return "error", flat[:90]
    if value != value:
        return "returned NaN", ""
    if kind == "two":
        if isinstance(data, dict) and data.get("is_unique") is False:
            return "gave both and said so (right)", "%r" % (data.get("all_irrs"),)
        return "gave one answer, %.6g, with no warning" % value, ""
    difference = abs(M(abs(value)) - abs(reference))
    relative = difference / abs(reference)
    if relative <= TOLERANCE or (server in ROUNDS_TO_CENTS and difference <= M("0.005")):
        return "agrees", "relative difference %s" % mp.nstr(relative, 2)
    return "DIFFERS", "got %r, reference %s, relative difference %s" % (
        value, mp.nstr(reference, 15), mp.nstr(relative, 2))


def main():
    rows = []
    for server, questions in SERVERS.items():
        command = os.path.join(BASE, server, "bin", server)
        os.environ["MEASURE_SERVER_" + server.upper().replace("-", "_")] = command
        try:
            with StdioServer(server) as running:
                for name, (tool, arguments, _key) in questions.items():
                    try:
                        is_error, payload, text = running.call(tool, arguments)
                        verdict, detail = judge(server, name, is_error, payload, text)
                    except Exception as exc:
                        verdict, detail = "error", "%s: %s" % (type(exc).__name__, str(exc)[:80])
                    rows.append((server, name, verdict, detail))
        except ServerError as exc:
            rows.append((server, "(start)", "did not start", str(exc)[:100]))
    print("| Server | Question | Result | Detail |")
    print("|---|---|---|---|")
    for row in rows:
        print("| %s | %s | %s | %s |" % tuple(str(cell).replace("|", "/") for cell in row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
