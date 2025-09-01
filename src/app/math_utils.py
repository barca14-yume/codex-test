"""Simple math utility functions.

These helpers demonstrate basic typed arithmetic operations with
minimal error handling and straightforward semantics.
"""

from __future__ import annotations


def add(a: float, b: float) -> float:
    """Return the sum of ``a`` and ``b``.

    Args:
        a: First addend.
        b: Second addend.

    Returns:
        The sum ``a + b`` as a float.
    """

    return a + b


def divide(a: float, b: float) -> float:
    """Return the quotient of ``a`` divided by ``b``.

    Raises ``ZeroDivisionError`` if ``b`` is zero.

    Args:
        a: Dividend.
        b: Divisor; must be non-zero.

    Returns:
        The result of ``a / b`` as a float.
    """

    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

