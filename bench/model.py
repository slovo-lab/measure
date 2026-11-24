"""Evaluate a measurement model such as 'V * I' with a tool's own objects.

A model is a short arithmetic expression. Only names, numbers and the
operators + - * / ** and unary minus are allowed, so a pairs file cannot make
the bench run arbitrary code. Written by Claude (AI).
"""
import ast
import operator

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


class ModelError(ValueError):
    """The model text is not an expression this bench accepts."""


def variables_in(model):
    """Names used in the model, in order of first appearance."""
    names = []
    for node in ast.walk(_parse(model)):
        if isinstance(node, ast.Name) and node.id not in names:
            names.append(node.id)
    return names


def _parse(model):
    try:
        return ast.parse(model, mode="eval")
    except SyntaxError as exc:
        raise ModelError("cannot read model %r: %s" % (model, exc)) from exc


def evaluate(model, values):
    """Evaluate the model. 'values' maps each variable name to a tool object."""
    return _eval(_parse(model).body, values)


def _eval(node, values):
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        return _BINARY[type(node.op)](_eval(node.left, values), _eval(node.right, values))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand, values)
    if isinstance(node, ast.Name):
        if node.id not in values:
            raise ModelError("model uses unknown variable %r" % node.id)
        return values[node.id]
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    raise ModelError("model contains something other than + - * / ** and names")
