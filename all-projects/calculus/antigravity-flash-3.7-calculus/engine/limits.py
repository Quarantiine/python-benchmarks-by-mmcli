"""
Limit Solver Engine
===================
Computes limits of symbolic expressions using direct substitution,
L'Hôpital's rule, and multi-epsilon perturbation sampling.
"""

from __future__ import annotations
import math
from typing import Union
from .ast_nodes import Node, Divide
from .simplifier import simplify
from .differentiator import diff


def limit(
    expr: Union[Node, str],
    var: str = "x",
    point: float = 0.0,
    direction: int = 0
) -> float:
    """
    Compute the limit of expr as var -> point.
    direction: 0 for two-sided, 1 for right-sided (x -> point+), -1 for left-sided (x -> point-).
    """
    if isinstance(expr, str):
        from .parser import parse_expr
        expr = parse_expr(expr)

    # 1. Direct substitution
    try:
        val = expr.evaluate({var: point})
        if not (math.isnan(val) or math.isinf(val)):
            return round(val, 8)
    except Exception:
        pass

    # 2. L'Hopital's rule if expression is a quotient
    curr = expr
    for _ in range(4):
        if isinstance(curr, Divide):
            num = curr.left
            den = curr.right
            try:
                num_val = num.evaluate({var: point})
                den_val = den.evaluate({var: point})
            except Exception:
                num_val, den_val = float('nan'), float('nan')

            # Check 0/0
            if abs(num_val) < 1e-9 and abs(den_val) < 1e-9:
                d_num = simplify(diff(num, var=var))
                d_den = simplify(diff(den, var=var))
                curr = Divide(d_num, d_den)
                try:
                    res = curr.evaluate({var: point})
                    if not (math.isnan(res) or math.isinf(res)):
                        return round(res, 8)
                except Exception:
                    continue
        else:
            break

    # 3. Multi-epsilon numerical perturbation sampling
    epsilons = [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]
    estimates = []

    for eps in epsilons:
        try:
            if direction > 0:
                v = expr.evaluate({var: point + eps})
            elif direction < 0:
                v = expr.evaluate({var: point - eps})
            else:
                vl = expr.evaluate({var: point - eps})
                vr = expr.evaluate({var: point + eps})
                v = (vl + vr) / 2.0

            if not (math.isnan(v) or math.isinf(v)) and abs(v) < 1e12:
                estimates.append(v)
        except Exception:
            continue

    if not estimates:
        raise ValueError(f"Could not evaluate limit of '{expr.to_infix()}' as {var} -> {point}")

    estimates.sort()
    med = estimates[len(estimates) // 2]
    return round(med, 8)
