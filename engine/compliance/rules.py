"""
rules.py — Regulatory schema definitions and check evaluation primitives.
"""

from typing import Dict, Any, Optional, Union


def evaluate_numeric_rule(
    val: Optional[Union[int, float]],
    operator: str,
    limit: Union[int, float]
) -> bool:
    """Evaluates a numeric condition (<=, >=, <, >, ==)."""
    if val is None:
        return False
    if operator == "<=":
        return val <= limit
    elif operator == ">=":
        return val >= limit
    elif operator == "<":
        return val < limit
    elif operator == ">":
        return val > limit
    elif operator == "==":
        return abs(val - limit) < 1e-5
    return False
