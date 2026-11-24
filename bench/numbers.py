"""Number strings from the pairs file. Written by Claude (AI)."""
from fractions import Fraction


def to_fraction(text):
    """'25.4', '-40', '1e-9' or '250/9' as an exact fraction."""
    if not isinstance(text, str):
        raise ValueError("numbers are written as strings, got %r" % (text,))
    return Fraction(text)


def to_float(text):
    """The nearest double to a number string: what a tool is actually given."""
    return float(to_fraction(text))
