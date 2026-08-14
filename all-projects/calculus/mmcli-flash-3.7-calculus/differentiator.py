"""
Symbolic Differentiation Engine & Calculus Utilities
====================================================
Provides high-level differentiation, higher-order derivatives, multivariable
calculus (gradient, Hessian), Taylor polynomial series approximations, tangent line
equations, Newton-Raphson root finding, and critical point analysis.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union

from ast_nodes import (
    Node, Constant, Variable, Add, Subtract, Multiply, Divide, Power, Negate,
    to_node
)
from simplifier import simplify
from tracker import DerivationTracker


def diff(
    expr: Union[Node, str],
    var: str = "x",
    order: int = 1,
    tracker: Optional[DerivationTracker] = None,
    simplify_result: bool = True
) -> Node:
    """
    Compute the symbolic derivative of `expr` with respect to `var` of given order.
    Optionally records step-by-step derivation in `tracker`.
    """
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    if order < 1:
        return expr

    curr: Node = expr
    for i in range(order):
        curr = curr.differentiate(var, tracker=tracker)
        if simplify_result:
            curr = simplify(curr)

    return curr


def higher_derivative(
    expr: Union[Node, str],
    var: str = "x",
    n: int = 1,
    order: Optional[int] = None,
    tracker: Optional[DerivationTracker] = None
) -> Node:
    """Compute the n-th derivative of `expr` with respect to `var`."""
    actual_order = order if order is not None else n
    return diff(expr, var=var, order=actual_order, tracker=tracker, simplify_result=True)


def partial_derivatives(expr: Union[Node, str], vars: List[str]) -> Dict[str, Node]:
    """Compute partial derivatives with respect to a list of variables."""
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)
    return {v: simplify(expr.differentiate(v)) for v in vars}


def gradient(expr: Union[Node, str], vars: List[str]) -> List[Node]:
    """Compute the symbolic gradient vector ∇f with respect to variables `vars`."""
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)
    return [simplify(expr.differentiate(v)) for v in vars]


def hessian(expr: Union[Node, str], vars: List[str]) -> List[List[Node]]:
    """Compute the Hessian matrix H_ij = d^2 f / (d x_i d x_j)."""
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)
    grad = gradient(expr, vars)
    matrix: List[List[Node]] = []
    for g_i in grad:
        row = [simplify(g_i.differentiate(v)) for v in vars]
        matrix.append(row)
    return matrix


def taylor_series(
    expr: Union[Node, str],
    var: str = "x",
    x0: float = 0.0,
    order: int = 4
) -> Node:
    """
    Generate the Taylor polynomial approximation around x = x0 of given order:
    T_n(x) = sum_{k=0}^n (f^(k)(x0) / k!) * (x - x0)^k
    """
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    v_node = Variable(var)
    shift = v_node if x0 == 0 else Subtract(v_node, Constant(x0))

    terms: List[Node] = []
    curr_deriv: Node = expr
    fact = 1

    for k in range(order + 1):
        if k > 0:
            fact *= k
            curr_deriv = simplify(curr_deriv.differentiate(var))

        try:
            c_val = curr_deriv.evaluate({var: x0})
        except Exception:
            c_val = float('nan')

        if not math.isnan(c_val) and not math.isinf(c_val) and abs(c_val) > 1e-12:
            coeff = c_val / fact
            coeff_node = Constant(coeff)

            if k == 0:
                terms.append(coeff_node)
            elif k == 1:
                terms.append(Multiply(coeff_node, shift))
            else:
                pow_term = Power(shift, Constant(k))
                terms.append(Multiply(coeff_node, pow_term))

    if not terms:
        return Constant(0)

    result: Node = terms[0]
    for term in terms[1:]:
        result = Add(result, term)

    return simplify(result)


def tangent_line(expr: Union[Node, str], x0: float, var: str = "x") -> Tuple[float, float, str]:
    """
    Compute the tangent line y = m*x + b at point x = x0.
    Returns (slope m, y-intercept b, equation string).
    """
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    y0 = expr.evaluate({var: x0})
    d_expr = diff(expr, var=var)
    slope = d_expr.evaluate({var: x0})
    b = y0 - slope * x0
    sign = "+" if b >= 0 else "-"
    eq_str = f"y = {slope:.4f}*{var} {sign} {abs(b):.4f}"
    return (slope, b, eq_str)


def find_roots_newton(
    expr: Union[Node, str],
    x0: float = 1.0,
    var: str = "x",
    max_iter: int = 50,
    tol: int | float = 1e-7
) -> Optional[float]:
    """
    Find a root of expr = 0 using the Newton-Raphson method:
    x_{n+1} = x_n - f(x_n) / f'(x_n)
    """
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    d_expr = diff(expr, var=var)
    curr_x = float(x0)

    for _ in range(max_iter):
        try:
            fx = expr.evaluate({var: curr_x})
            dfx = d_expr.evaluate({var: curr_x})
        except Exception:
            return None

        if abs(dfx) < 1e-12:
            return None

        if abs(fx) < tol:
            return curr_x

        curr_x = curr_x - (fx / dfx)

    return curr_x if abs(expr.evaluate({var: curr_x})) < 1e-3 else None


def critical_points(
    expr: Union[Node, str],
    domain_or_var: Any = None,
    var: str = "x",
    samples: int = 500,
    domain: Optional[Tuple[float, float]] = None,
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Find critical points where f'(x) = 0 and classify them (local min, local max, inflection).
    """
    if isinstance(domain_or_var, (tuple, list)):
        domain = tuple(domain_or_var)
    elif isinstance(domain_or_var, str):
        var = domain_or_var

    if domain is None:
        domain = (x_min if x_min is not None else -10.0, x_max if x_max is not None else 10.0)

    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    d1 = diff(expr, var=var)
    d2 = diff(d1, var=var)

    a, b = domain
    step = (b - a) / samples
    found_xs: List[float] = []

    # Sample domain and apply Newton-Raphson when sign changes or near zero
    prev_val = None
    for i in range(samples + 1):
        x_val = a + i * step
        try:
            val = d1.evaluate({var: x_val})
        except Exception:
            continue

        if prev_val is not None and ((prev_val < 0 < val) or (prev_val > 0 > val) or abs(val) < 1e-2):
            root = find_roots_newton(d1, x0=x_val, var=var)
            if root is not None and a <= root <= b:
                if not any(math.isclose(root, existing, abs_tol=1e-3) for existing in found_xs):
                    found_xs.append(root)
        prev_val = val

    results = []
    for x_c in sorted(found_xs):
        try:
            y_c = expr.evaluate({var: x_c})
            d2_val = d2.evaluate({var: x_c})
        except Exception:
            continue

        if d2_val > 1e-5:
            nature = "local minimum"
        elif d2_val < -1e-5:
            nature = "local maximum"
        else:
            nature = "saddle / inflection"

        results.append({
            "x": round(x_c, 5),
            "y": round(y_c, 5),
            "f_double_prime": round(d2_val, 5),
            "f2": round(d2_val, 5),
            "nature": nature,
            "classification": nature
        })

    return results


def find_all_roots(
    expr: Union[Node, str],
    domain: Tuple[float, float] = (-10.0, 10.0),
    var: str = "x",
    samples: int = 500
) -> List[float]:
    """Find real roots of expr = 0 across a domain interval."""
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    a, b = domain
    step = (b - a) / samples
    roots: List[float] = []

    prev_val = None
    for i in range(samples + 1):
        x_val = a + i * step
        try:
            val = expr.evaluate({var: x_val})
        except Exception:
            continue

        if prev_val is not None and ((prev_val < 0 < val) or (prev_val > 0 > val) or abs(val) < 1e-2):
            root = find_roots_newton(expr, x0=x_val, var=var)
            if root is not None and a <= root <= b:
                if not any(math.isclose(root, existing, abs_tol=1e-3) for existing in roots):
                    roots.append(round(root, 5))
        prev_val = val

    return sorted(roots)


# Aliases
find_roots = find_all_roots
find_critical_points = critical_points
differentiate = diff


def newton_raphson(
    expr: Union[Node, str],
    var: str = "x",
    x0: float = 1.0,
    max_iter: int = 50,
    tol: int | float = 1e-7
) -> Optional[float]:
    """Alias for find_roots_newton with flexible arg ordering."""
    return find_roots_newton(expr, x0=x0, var=var, max_iter=max_iter, tol=tol)

