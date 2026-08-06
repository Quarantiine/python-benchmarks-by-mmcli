"""Limit calculation engine for AST nodes using evaluation and symmetric perturbation."""

import math
from .ast import Node


def limit(node: Node, var: str = "x", point: float = 0.0) -> float:
    """Evaluate limit of AST node as var approaches point."""
    point = float(point)

    # 1. Try direct evaluation
    try:
        val = node.evaluate({var: point})
        if not math.isnan(val) and not math.isinf(val):
            return float(val)
    except Exception:
        pass

    # 2. Symmetric numerical sampling near point for removable singularities / 0/0 limits
    for eps in [1e-4, 1e-6, 1e-8]:
        try:
            v_left = node.evaluate({var: point - eps})
            v_right = node.evaluate({var: point + eps})
            if not math.isnan(v_left) and not math.isnan(v_right):
                if not math.isinf(v_left) and not math.isinf(v_right):
                    avg = (v_left + v_right) / 2.0
                    return float(avg)
        except Exception:
            continue

    raise ValueError(f"Could not compute limit of expression at {var} = {point}")
