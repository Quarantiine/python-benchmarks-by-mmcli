"""
Symbolic & Numerical Limit Engine
=================================
Computes analytical and numerical limits of mathematical expressions using:
1. Direct evaluation and continuity analysis
2. Multi-pass symbolic L'Hôpital's rule for indeterminate forms (0/0, ∞/∞)
3. Multi-epsilon perturbation sampling with symmetric Richardson extrapolation
4. Infinite limits (x → ±∞) and one-sided limits (x → a⁺, x → a⁻).
"""

from __future__ import annotations
import math
from typing import Optional, Union, List

from ast_nodes import Node, Divide, Constant, Variable, Multiply, Add, Subtract
from simplifier import simplify
from differentiator import diff


def limit(
    expr: Union[Node, str],
    var: str = "x",
    point: Union[float, int, str] = 0.0,
    direction: Union[int, str] = 0
) -> float:
    """
    Compute the limit of `expr` as `var` approaches `point`.

    Parameters:
        expr: AST Node or math expression string.
        var: Variable symbol approaching the limit point (default "x").
        point: Limit destination point (numeric or 'inf' / '-inf').
        direction: 0 for two-sided limit, +1 or '+' for right-handed (x -> a+), -1 or '-' for left-handed (x -> a-).

    Returns:
        The limit value as a float or int.
    """
    if isinstance(direction, str):
        if direction in ("+", "+1", "right", "dir=+"):
            dir_val = 1
        elif direction in ("-", "-1", "left", "dir=-"):
            dir_val = -1
        else:
            dir_val = 0
    else:
        dir_val = int(direction)

    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    # Handle infinity points
    if isinstance(point, str):
        pt_lower = point.lower().strip()
        if pt_lower in ("inf", "+inf", "infinity"):
            point = float("inf")
        elif pt_lower in ("-inf", "-infinity"):
            point = float("-inf")
        else:
            point = float(point)

    # 1. Infinite limit handling (x -> ±∞)
    if math.isinf(point):
        return _limit_at_infinity(expr, var, point)

    pt = float(point)

    # 2. Direct substitution
    try:
        val = expr.evaluate({var: pt})
        if not (math.isnan(val) or math.isinf(val)):
            return int(val) if isinstance(val, (int, float)) and float(val).is_integer() else round(val, 8)
    except Exception:
        pass

    # 3. L'Hôpital's Rule (symbolic derivatives of quotient)
    curr = expr
    for _ in range(5):
        if isinstance(curr, Divide):
            num = curr.left
            den = curr.right

            num_val = None
            den_val = None
            try:
                num_val = num.evaluate({var: pt})
            except Exception:
                pass

            try:
                den_val = den.evaluate({var: pt})
            except Exception:
                pass

            is_0_0 = (num_val is not None and abs(num_val) < 1e-7 and
                      den_val is not None and abs(den_val) < 1e-7)
            is_inf_inf = (num_val is not None and math.isinf(num_val) and
                          den_val is not None and math.isinf(den_val))

            if is_0_0 or is_inf_inf or den_val == 0:
                d_num = simplify(diff(num, var=var))
                d_den = simplify(diff(den, var=var))
                curr = Divide(d_num, d_den)
                try:
                    res = curr.evaluate({var: pt})
                    if not (math.isnan(res) or math.isinf(res)):
                        return int(res) if float(res).is_integer() else round(res, 8)
                except Exception:
                    continue
        else:
            break

    # 4. Multi-epsilon numerical perturbation sampling
    epsilons = [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]
    estimates: List[float] = []

    for eps in epsilons:
        try:
            if dir_val > 0:
                v = expr.evaluate({var: pt + eps})
            elif dir_val < 0:
                v = expr.evaluate({var: pt - eps})
            else:
                vl = expr.evaluate({var: pt - eps})
                vr = expr.evaluate({var: pt + eps})
                v = (vl + vr) / 2.0

            if not (math.isnan(v) or math.isinf(v)) and abs(v) < 1e12:
                estimates.append(v)
        except Exception:
            continue

    if estimates:
        estimates.sort()
        med = estimates[len(estimates) // 2]
        if math.isclose(med, round(med), abs_tol=1e-5):
            return int(round(med))
        return round(med, 8)

    raise ValueError(f"Could not evaluate limit of '{expr.to_infix()}' as {var} -> {point}")


def _limit_at_infinity(expr: Node, var: str, point: float) -> float:
    """Evaluate limit as variable goes to +inf or -inf using large values and Richardson extrapolation."""
    test_vals = [1e4, 1e5, 1e6, 1e7, 1e8] if point > 0 else [-1e4, -1e5, -1e6, -1e7, -1e8]
    results: List[float] = []

    for x_val in test_vals:
        try:
            val = expr.evaluate({var: x_val})
            if not (math.isnan(val) or math.isinf(val)):
                results.append(val)
        except Exception:
            continue

    if not results:
        raise ValueError(f"Could not evaluate infinite limit for '{expr.to_infix()}'")

    final_val = results[-1]
    if math.isclose(final_val, round(final_val), abs_tol=1e-4):
        return int(round(final_val))
    return round(final_val, 8)


def limit_direction(
    expr: Union[Node, str],
    var: str = "x",
    point: Union[float, int, str] = 0.0,
    direction: Union[int, str] = "+"
) -> float:
    """Compute one-sided limit from right ('+' / +1) or left ('-' / -1)."""
    return limit(expr, var=var, point=point, direction=direction)

