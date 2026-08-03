"""
Symbolic Limit Engine.

Evaluates symbolic limits via direct substitution, algebraic cancellation,
L'Hôpital's Rule for indeterminate forms (0/0, inf/inf), standard limit identities,
and one-sided numeric probe validation.
"""

import math
from typing import Union, Optional, Tuple
from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Exp, Ln, Sqrt, Abs
)
from calculus.simplify import simplify
from calculus.diff import diff


def limit(
    expr: Expr,
    var: Union[str, Symbol],
    point: Union[float, int, str, Expr],
    direction: str = "both"
) -> Union[Expr, float]:
    """
    Evaluate the limit of expr as var approaches point.

    :param expr: Symbolic expression AST.
    :param var: Variable symbol or name approaching point.
    :param point: Limit target value (number or 'inf' / '-inf').
    :param direction: Approach direction ('both', 'left', 'right').
    :return: Symbolic expression or float value representing the limit.
    """
    var_name = var.name if isinstance(var, Symbol) else str(var)
    
    # Handle infinite limit targets
    if isinstance(point, str) and point.lower() in ("inf", "infinity", "+inf"):
        return _limit_at_infinity(expr, var_name, positive=True)
    if isinstance(point, str) and point.lower() in ("-inf", "-infinity"):
        return _limit_at_infinity(expr, var_name, positive=False)

    pt_expr = point if isinstance(point, Expr) else Const(point)

    # 1. Direct Substitution
    try:
        sub_expr = simplify(expr.subs(var_name, pt_expr))
        val = sub_expr.eval()
        if not (math.isnan(val) or math.isinf(val)):
            return val
    except (ZeroDivisionError, ValueError):
        pass

    # 2. Indeterminate form 0/0 or inf/inf -> Apply L'Hôpital's Rule or simplification
    if isinstance(expr, Div):
        num, den = expr.left, expr.right

        num_val, num_err = _try_eval_at(num, var_name, pt_expr)
        den_val, den_err = _try_eval_at(den, var_name, pt_expr)

        # 0/0 Indeterminate form
        if (num_val == 0 or num_err) and (den_val == 0 or den_err):
            # Try algebraic cancellation first
            cancelled = _try_cancel_factor(num, den, var_name, pt_expr)
            if cancelled is not None:
                return limit(cancelled, var_name, point, direction)

            # Apply L'Hôpital's Rule: lim f/g = lim f'/g'
            d_num = diff(num, var_name)
            d_den = diff(den, var_name)
            lhopital_expr = Div(d_num, d_den)
            return limit(lhopital_expr, var_name, point, direction)

    # 3. Numeric probe fallback for limits that are hard symbolically
    probe_val = _numeric_limit_probe(expr, var_name, pt_expr.eval(), direction)
    if probe_val is not None:
        return probe_val

    raise ValueError(f"Unable to determine symbolic limit for {expr} as {var_name} -> {point}")


def _try_eval_at(expr: Expr, var: str, point: Expr) -> Tuple[Optional[float], bool]:
    """Helper to safely evaluate expr at var=point. Returns (val, is_error)."""
    try:
        subbed = simplify(expr.subs(var, point))
        v = subbed.eval()
        return (v, False)
    except Exception:
        return (None, True)


def _try_cancel_factor(num: Expr, den: str, var: str, point: Expr) -> Optional[Expr]:
    """Attempt polynomial factor cancellation for (x - x0)."""
    # Simple polynomial division check
    try:
        x0 = point.eval()
        # If both num and den are polynomial forms like (x - x0)*P(x)
        # We try dividing both by (x - x0)
        factor = Sub(Symbol(var), Const(x0))
        # Simplify num/factor and den/factor
        s_num = simplify(Div(num, factor))
        s_den = simplify(Div(den, factor))
        if not isinstance(s_num, Div) and not isinstance(s_den, Div):
            return Div(s_num, s_den)
    except Exception:
        pass
    return None


def _limit_at_infinity(expr: Expr, var: str, positive: bool) -> float:
    """Evaluate limit as var approaches +infinity or -infinity."""
    # Check degree ratio for rational expressions
    if isinstance(expr, Div):
        num, den = expr.left, expr.right
        deg_num = _poly_degree(num, var)
        deg_den = _poly_degree(den, var)

        if deg_num is not None and deg_den is not None:
            if deg_num < deg_den:
                return 0.0
            if deg_num == deg_den:
                c_num = _poly_leading_coef(num, var)
                c_den = _poly_leading_coef(den, var)
                if c_num is not None and c_den is not None and c_den != 0:
                    return c_num / c_den
            if deg_num > deg_den:
                c_num = _poly_leading_coef(num, var) or 1.0
                c_den = _poly_leading_coef(den, var) or 1.0
                sign = 1.0 if (c_num * c_den) > 0 else -1.0
                return float('inf') * sign

    # Probe at large value x = 1e6
    probe_x = 1e6 if positive else -1e6
    try:
        val = expr.eval({var: probe_x})
        if math.isclose(val, 0.0, abs_tol=1e-4):
            return 0.0
        return round(val, 6)
    except Exception:
        return float('inf') if positive else float('-inf')


def _poly_degree(expr: Expr, var: str) -> Optional[int]:
    """Get degree of polynomial in var."""
    if var not in expr.free_symbols():
        return 0
    if isinstance(expr, Symbol) and expr.name == var:
        return 1
    if isinstance(expr, Pow) and isinstance(expr.left, Symbol) and expr.left.name == var and isinstance(expr.right, Const):
        return int(expr.right.value)
    if isinstance(expr, Add):
        d1 = _poly_degree(expr.left, var)
        d2 = _poly_degree(expr.right, var)
        if d1 is not None and d2 is not None:
            return max(d1, d2)
    if isinstance(expr, Mul):
        d1 = _poly_degree(expr.left, var)
        d2 = _poly_degree(expr.right, var)
        if d1 is not None and d2 is not None:
            return d1 + d2
    return None


def _poly_leading_coef(expr: Expr, var: str) -> Optional[float]:
    """Get leading coefficient of polynomial in var."""
    deg = _poly_degree(expr, var)
    if deg is None:
        return None
    if deg == 0:
        return expr.eval() if not expr.free_symbols() else None
    if isinstance(expr, Symbol) and expr.name == var and deg == 1:
        return 1.0
    if isinstance(expr, Mul):
        if isinstance(expr.left, Const):
            return float(expr.left.value) * (_poly_leading_coef(expr.right, var) or 1.0)
        if isinstance(expr.right, Const):
            return float(expr.right.value) * (_poly_leading_coef(expr.left, var) or 1.0)
    return 1.0


def _numeric_limit_probe(expr: Expr, var: str, x0: float, direction: str) -> Optional[float]:
    """Numeric probe limit as x -> x0 using sequence of decreasing epsilons."""
    epsilons = [1e-4, 1e-6, 1e-8]
    vals = []

    for eps in epsilons:
        x_val = x0 + eps if direction == "right" else (x0 - eps if direction == "left" else x0 + eps)
        try:
            v = expr.eval({var: x_val})
            vals.append(v)
        except Exception:
            pass

    if len(vals) >= 2:
        if math.isclose(vals[-1], vals[-2], rel_tol=1e-3, abs_tol=1e-4):
            # Round nicely to integer or standard float
            res = vals[-1]
            if math.isclose(res, round(res), abs_tol=1e-4):
                return float(round(res))
            return round(res, 6)
        if vals[-1] > 1e3 and vals[-1] > 10 * vals[-2]:
            return float('inf')
        if vals[-1] < -1e3 and vals[-1] < 10 * vals[-2]:
            return float('-inf')

    return None
