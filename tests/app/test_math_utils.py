"""Tests for app.math_utils.

Mirrors the structure under ``src/app``.
"""

from __future__ import annotations

import pytest

from app.math_utils import add, divide


def test_add_basic() -> None:
    assert add(1.2, 3.4) == pytest.approx(4.6)


def test_add_types() -> None:
    assert add(1, 2) == 3
    assert add(1, 2.5) == pytest.approx(3.5)
    assert add(1.5, 2) == pytest.approx(3.5)


def test_divide_basic() -> None:
    assert divide(4, 2) == 2
    assert divide(5, 2) == 2.5


def test_divide_zero_raises() -> None:
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

