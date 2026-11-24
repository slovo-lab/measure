#!/usr/bin/env python3
"""Check that a reference-pairs file follows the format in FORMAT.md.

Uses only the Python standard library. Written by Claude (AI).

Usage: python3 tools/check_pairs.py [pairs/pairs.json]
Exit status 0 if the file is valid, 1 otherwise.
"""
import json
import re
import sys
from fractions import Fraction

FORMAT_VERSION = 1

CATEGORIES = {
    "unit-conversion",
    "dimensional-safety",
    "type-a",
    "type-b",
    "combined",
    "degrees-of-freedom",
    "reporting",
}

# For each task: the output names a reference must give, exactly.
TASK_OUTPUTS = {
    "convert": {"value"},
    "type_a": {"mean", "standard_uncertainty"},
    "type_b": {"standard_uncertainty"},
    "propagate": {"value", "combined_standard_uncertainty"},
    "add": {"value"},
    "effective_dof": {"effective_degrees_of_freedom"},
    "round": {"value"},
}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def parse_number(text):
    """Parse a number written as a string: '25.4', '-40', '1e-9' or '250/9'."""
    if not isinstance(text, str):
        raise ValueError("numbers are written as strings, got %r" % (text,))
    return Fraction(text)


def _num(errors, where, obj, key):
    if key not in obj:
        errors.append("%s: missing '%s'" % (where, key))
        return None
    try:
        return parse_number(obj[key])
    except (ValueError, ZeroDivisionError) as exc:
        errors.append("%s: '%s' is not a number string (%s)" % (where, key, exc))
        return None


def _text(errors, where, obj, key):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append("%s: '%s' must be a non-empty string" % (where, key))
        return None
    return value


def _check_inputs(errors, where, task, inputs):
    if not isinstance(inputs, dict):
        errors.append("%s: 'inputs' must be an object" % where)
        return
    if task == "convert":
        _num(errors, where, inputs, "value")
        _text(errors, where, inputs, "unit")
        _text(errors, where, inputs, "to_unit")
    elif task == "type_a":
        readings = inputs.get("readings")
        if not isinstance(readings, list) or len(readings) < 2:
            errors.append("%s: 'readings' must be a list of at least 2" % where)
        else:
            for i, r in enumerate(readings):
                _num(errors, "%s readings[%d]" % (where, i), {"v": r}, "v")
        _text(errors, where, inputs, "unit")
    elif task == "type_b":
        distribution = inputs.get("distribution")
        if distribution not in ("rectangular", "triangular", "normal"):
            errors.append("%s: unknown 'distribution'" % where)
        if distribution == "normal":
            p = _num(errors, where, inputs, "coverage_probability")
            if p is not None and not 0 < p < 1:
                errors.append("%s: 'coverage_probability' must be between 0 and 1" % where)
        elif "coverage_probability" in inputs:
            errors.append("%s: 'coverage_probability' is only for a normal distribution" % where)
        hw = _num(errors, where, inputs, "half_width")
        if hw is not None and hw <= 0:
            errors.append("%s: 'half_width' must be positive" % where)
        _text(errors, where, inputs, "unit")
    elif task == "effective_dof":
        components = inputs.get("components")
        if not isinstance(components, list) or len(components) < 2:
            errors.append("%s: 'components' must be a list of at least 2" % where)
        else:
            for i, component in enumerate(components):
                cwhere = "%s components[%d]" % (where, i)
                if not isinstance(component, dict):
                    errors.append("%s: must be an object" % cwhere)
                    continue
                c = _num(errors, cwhere, component, "contribution")
                nu = _num(errors, cwhere, component, "degrees_of_freedom")
                if c is not None and c <= 0:
                    errors.append("%s: 'contribution' must be positive" % cwhere)
                if nu is not None and nu <= 0:
                    errors.append("%s: 'degrees_of_freedom' must be positive" % cwhere)
        _text(errors, where, inputs, "unit")
    elif task == "round":
        _num(errors, where, inputs, "value")
        digits = inputs.get("significant_digits")
        if isinstance(digits, bool) or not isinstance(digits, int) or digits < 1:
            errors.append("%s: 'significant_digits' must be a whole number, 1 or more" % where)
    elif task == "add":
        terms = inputs.get("terms")
        if not isinstance(terms, list) or len(terms) < 2:
            errors.append("%s: 'terms' must be a list of at least 2" % where)
        else:
            for i, term in enumerate(terms):
                twhere = "%s terms[%d]" % (where, i)
                if not isinstance(term, dict):
                    errors.append("%s: must be an object" % twhere)
                    continue
                _num(errors, twhere, term, "value")
                _text(errors, twhere, term, "unit")
    elif task == "propagate":
        _text(errors, where, inputs, "model")
        variables = inputs.get("variables")
        if not isinstance(variables, dict) or not variables:
            errors.append("%s: 'variables' must be a non-empty object" % where)
            variables = {}
        for name, var in variables.items():
            vwhere = "%s variable %s" % (where, name)
            if not NAME_RE.match(name):
                errors.append("%s: bad variable name" % vwhere)
            if not isinstance(var, dict):
                errors.append("%s: must be an object" % vwhere)
                continue
            _num(errors, vwhere, var, "value")
            u = _num(errors, vwhere, var, "standard_uncertainty")
            if u is not None and u < 0:
                errors.append("%s: negative standard uncertainty" % vwhere)
            _text(errors, vwhere, var, "unit")
        covs = inputs.get("covariances")
        if not isinstance(covs, list):
            errors.append("%s: 'covariances' must be a list (may be empty)" % where)
            covs = []
        for i, cov in enumerate(covs):
            cwhere = "%s covariances[%d]" % (where, i)
            if not isinstance(cov, dict):
                errors.append("%s: must be an object" % cwhere)
                continue
            between = cov.get("between")
            if (not isinstance(between, list) or len(between) != 2
                    or between[0] == between[1]
                    or any(b not in variables for b in between)):
                errors.append("%s: 'between' must name two different variables" % cwhere)
                between = None
            c = _num(errors, cwhere, cov, "value")
            _text(errors, cwhere, cov, "unit")
            if between and c is not None:
                try:
                    u1 = parse_number(variables[between[0]]["standard_uncertainty"])
                    u2 = parse_number(variables[between[1]]["standard_uncertainty"])
                except (KeyError, TypeError, ValueError):
                    continue
                if abs(c) > u1 * u2:
                    errors.append("%s: |covariance| exceeds u1*u2, which is impossible" % cwhere)


def _check_reference(errors, where, task, reference):
    if not isinstance(reference, dict):
        errors.append("%s: 'reference' must be an object" % where)
        return
    if "outcome" in reference and reference["outcome"] != "refuse":
        errors.append("%s: the only known 'outcome' is 'refuse'" % where)
        return
    if reference.get("outcome") == "refuse":
        if "outputs" in reference:
            errors.append("%s: a 'refuse' reference has no outputs" % where)
        return
    outputs = reference.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        errors.append("%s: 'reference.outputs' must be a non-empty list" % where)
        return
    names = []
    for out in outputs:
        if not isinstance(out, dict):
            errors.append("%s: each output must be an object" % where)
            continue
        name = out.get("name")
        names.append(name)
        owhere = "%s output %s" % (where, name)
        _num(errors, owhere, out, "value")
        _text(errors, owhere, out, "unit")
        if not isinstance(out.get("exact"), bool):
            errors.append("%s: 'exact' must be true or false" % owhere)
        tol = out.get("tolerance")
        if not isinstance(tol, dict) or tol.get("kind") not in ("relative", "absolute"):
            errors.append("%s: 'tolerance.kind' must be 'relative' or 'absolute'" % owhere)
        else:
            t = _num(errors, owhere + " tolerance", tol, "value")
            if t is not None and t <= 0:
                errors.append("%s: tolerance must be positive" % owhere)
    expected = TASK_OUTPUTS.get(task)
    if expected is not None and (set(names) != expected or len(names) != len(expected)):
        errors.append("%s: task '%s' needs exactly the outputs %s, got %s"
                      % (where, task, sorted(expected), names))


def check_document(doc):
    """Return a list of error strings; empty if the document is valid."""
    errors = []
    if not isinstance(doc, dict):
        return ["top level must be an object"]
    if doc.get("format_version") != FORMAT_VERSION:
        errors.append("format_version must be %d" % FORMAT_VERSION)
    pairs = doc.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        errors.append("'pairs' must be a non-empty list")
        return errors
    seen = set()
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            errors.append("pairs[%d]: must be an object" % index)
            continue
        pid = pair.get("id")
        where = "pair %s" % (pid if isinstance(pid, str) else "#%d" % index)
        if not isinstance(pid, str) or not ID_RE.match(pid):
            errors.append("%s: 'id' must be lower-case words joined by hyphens" % where)
        elif pid in seen:
            errors.append("%s: duplicate id" % where)
        else:
            seen.add(pid)
        if pair.get("category") not in CATEGORIES:
            errors.append("%s: unknown category %r" % (where, pair.get("category")))
        _text(errors, where, pair, "question")
        _text(errors, where, pair, "derivation")
        task = pair.get("task")
        if task not in TASK_OUTPUTS:
            errors.append("%s: unknown task %r" % (where, task))
        else:
            _check_inputs(errors, where, task, pair.get("inputs"))
        _check_reference(errors, where, task, pair.get("reference"))
        sources = pair.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append("%s: at least one source is required" % where)
            continue
        for i, src in enumerate(sources):
            swhere = "%s sources[%d]" % (where, i)
            if not isinstance(src, dict):
                errors.append("%s: must be an object" % swhere)
                continue
            _text(errors, swhere, src, "document")
            _text(errors, swhere, src, "locator")
            url = src.get("url")
            if url is not None and not (isinstance(url, str) and url.startswith("https://")):
                errors.append("%s: 'url', if given, must start with https://" % swhere)
            checked = src.get("checked")
            if not isinstance(checked, str) or not DATE_RE.match(checked):
                errors.append("%s: 'checked' must be a date YYYY-MM-DD" % swhere)
    return errors


def main(argv):
    path = argv[1] if len(argv) > 1 else "pairs/pairs.json"
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, ValueError) as exc:
        print("cannot read %s: %s" % (path, exc))
        return 1
    errors = check_document(doc)
    for error in errors:
        print(error)
    if errors:
        print("%d problem(s) in %s" % (len(errors), path))
        return 1
    print("%s: %d pairs, format valid" % (path, len(doc["pairs"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
