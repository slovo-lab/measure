"""Evaluate the `model` expression of a `propagate` pair.

The expression is plain arithmetic over named variables: + - * / ** and
parentheses. It is evaluated on whatever objects the adapter supplies for the
variables (for example numbers with uncertainty), so the tool under test does
the arithmetic. Anything else in the expression is rejected.

Written by Claude (AI).
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
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class ModelError(ValueError):
    """The model expression uses something that is not allowed."""


def evaluate(expression, variables):
    """Return the value of `expression` with names taken from `variables`."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ModelError("cannot parse model %r: %s" % (expression, exc))
    return _walk(tree.body, variables)


def _walk(node, variables):
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        return _BINARY[type(node.op)](_walk(node.left, variables), _walk(node.right, variables))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_walk(node.operand, variables))
    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise ModelError("unknown variable %r in model" % node.id)
        return variables[node.id]
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    raise ModelError("not allowed in a model: %s" % type(node).__name__)
