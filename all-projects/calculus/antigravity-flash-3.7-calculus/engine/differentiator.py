"""
Symbolic Differentiation Engine & Calculus Utilities
====================================================
Provides high-level differentiation, higher-order derivatives, multivariable
calculus (gradient, Hessian), Taylor approximations, tangent lines, root finding,
and critical point analysis.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from .ast_nodes import (
    Node, Constant, Variable, Add, Subtract, Multiply, Divide, Power, Negate,
    _to_node
)
from .simplifier import simplify
from .tracker import DerivationTracker


def diff(
    expr: Union[Node, str],
    var: str = "x",
    order: int = 1,
    tracker: Optional[DerivationTracker] = None,
    simplify_result: bool = True
) -> Node:
    """Compute the symbolic derivative of `expr` with respect to `var` of given order."""
    if isinstance(expr, str):
        from .parser import parse_expr
        expr = parse_expr(expr)

    curr: Node = expr
    for i in range(order):
        if order > 1 and tracker:
            step_header = f"--- Derivative Order {i + 1} of {order} ---"
            # Optional grouping can be done in tracker
        curr = curr.differentiate(var, tracker=tracker)
        if simplify_result:
            curr = simplify(curr)

    return curr


def higher_derivative(
    expr: Node,
    var: str,
    n: int,
    tracker: Optional[DerivationTracker] = None
) -> Node:
    """Compute the n-th derivative of `expr` with respect to `var`."""
    return diff(expr, var=var, order=n, tracker=tracker, simplify_result=True)


def partial_derivatives(expr: Node, vars: List[str]) -> Dict[str, Node]:
    """Compute partial derivatives with respect to a list of variables."""
    return {v: simplify(expr.differentiate(v)) for v in vars}


def gradient(expr: Node, vars: List[str]) -> List[Node]:
    """Compute the symbolic gradient vector ∇f with respect to variables `vars`."""
    return [simplify(expr.differentiate(v)) for v in vars]


def hessian(expr: Node, vars: List[str]) -> List[List[Node]]:
    """Compute the Hessian matrix H_ij = d^2 f / (d x_i d x_j)."""
    matrix: List[List[Node]] = []
    grad = gradient(expr, vars)
    for i, g_i in enumerate(grad):
        row = [simplify(g_i.differentiate(v)) for v in vars]
        matrix.append(row)
    return matrix


def taylor_series(
    expr: Node,
    var: str = "x",
    x0: float = 0.0,
    order: int = 4
) -> Node:
    """
    Generate the Taylor polynomial approximation around x = x0 of given order:
    T_n(x) = sum_{k=0}^n (f^(k)(x0) / k!) * (x - x0)^k
    """
    v_node = Variable(var)
    shift = v_node if x0 == 0 else Subtract(v_node, Constant(x0))
    
    terms: List[Node] = []
    curr_deriv = expr
    fact = 1
    
    for k in range(order + 1):
        if k > 0:
            fact *= k
            curr_deriv = simplify(curr_deriv.differentiate(var))
        
        try:
            c_val = curr_deriv.evaluate({var: x0})
        except Exception:
            c_val = float('nan')
            
        if math.isnan(c_val) or math.isinf(c_val):
            continue
        if abs(c_val) < 1e-12:
            continue
            
        coeff = c_val / fact
        if k == 0:
            terms.append(Constant(coeff))
        elif k == 1:
            terms.append(Multiply(Constant(coeff), shift))
        else:
            term_power = Power(shift, Constant(k))
            terms.append(Multiply(Constant(coeff), term_power))
            
    if not terms:
        return Constant(0)
        
    res = terms[0]
    for t in terms[1:]:
        res = Add(res, t)
    return simplify(res)


def tangent_line(
    expr: Node,
    var: str = "x",
    x0: float = 0.0
) -> Tuple[Node, float, float]:
    """
    Compute the tangent line equation at x = x0:
    y = m * (x - x0) + y0
    Returns: (tangent_node, slope_m, y_intercept_b)
    """
    y0 = expr.evaluate({var: x0})
    d_expr = simplify(expr.differentiate(var))
    m = d_expr.evaluate({var: x0})
    
    # y = m*x + (y0 - m*x0)
    b = y0 - m * x0
    v_node = Variable(var)
    line_expr = simplify(Add(Multiply(Constant(m), v_node), Constant(b)))
    return (line_expr, m, b)


def normal_line(
    expr: Node,
    var: str = "x",
    x0: float = 0.0
) -> Tuple[Optional[Node], float, float]:
    """
    Compute the normal line equation at x = x0:
    slope = -1/m
    Returns: (normal_node, slope_norm, y_intercept_b)
    """
    y0 = expr.evaluate({var: x0})
    d_expr = simplify(expr.differentiate(var))
    m = d_expr.evaluate({var: x0})
    
    if abs(m) < 1e-12:
        # Vertical normal line x = x0
        return (None, float('inf'), x0)
        
    m_norm = -1.0 / m
    b = y0 - m_norm * x0
    v_node = Variable(var)
    line_expr = simplify(Add(Multiply(Constant(m_norm), v_node), Constant(b)))
    return (line_expr, m_norm, b)


def find_roots(
    expr: Node,
    var: str = "x",
    x_min: float = -10.0,
    x_max: float = 10.0,
    num_samples: int = 200,
    tol: float = 1e-7,
    max_iter: int = 50
) -> List[float]:
    """Find roots of expr = 0 in [x_min, x_max] using Newton-Raphson."""
    roots: List[float] = []
    d_expr = simplify(expr.differentiate(var))
    step = (x_max - x_min) / num_samples
    
    for i in range(num_samples):
        x = x_min + i * step
        # Newton-Raphson iteration
        for _ in range(max_iter):
            try:
                fx = expr.evaluate({var: x})
                dfx = d_expr.evaluate({var: x})
            except Exception:
                break
                
            if math.isnan(fx) or math.isnan(dfx) or abs(dfx) < 1e-14:
                break
                
            if abs(fx) < tol:
                # Root found
                if x_min - 0.1 <= x <= x_max + 0.1:
                    # Check duplicate
                    if not any(math.isclose(x, r, abs_tol=1e-4) for r in roots):
                        roots.append(round(x, 6))
                break
                
            x_next = x - fx / dfx
            if abs(x_next - x) < tol:
                x = x_next
                if x_min - 0.1 <= x <= x_max + 0.1:
                    if not any(math.isclose(x, r, abs_tol=1e-4) for r in roots):
                        roots.append(round(x, 6))
                break
            x = x_next
            
    return sorted(roots)


def find_critical_points(
    expr: Node,
    var: str = "x",
    x_min: float = -10.0,
    x_max: float = 10.0
) -> List[Dict[str, Any]]:
    """
    Find critical points where f'(x) = 0 and classify them using f''(x).
    Returns list of dicts with: x, y, type ('local_min', 'local_max', 'inflection', 'unknown').
    """
    d1 = simplify(expr.differentiate(var))
    d2 = simplify(d1.differentiate(var))
    
    crit_x = find_roots(d1, var=var, x_min=x_min, x_max=x_max)
    results = []
    
    for x in crit_x:
        try:
            y = expr.evaluate({var: x})
            f2 = d2.evaluate({var: x})
        except Exception:
            continue
            
        if math.isnan(y) or math.isnan(f2):
            continue
            
        if f2 > 1e-6:
            classification = "Local Minimum"
        elif f2 < -1e-6:
            classification = "Local Maximum"
        else:
            classification = "Inflection / Saddle Point"
            
        results.append({
            "x": x,
            "y": round(y, 6),
            "f2": round(f2, 6),
            "classification": classification
        })
        
    return results


def definite_integral_approx(
    expr: Node,
    var: str = "x",
    a: float = 0.0,
    b: float = 1.0,
    n: int = 1000
) -> float:
    """
    Numerically approximate the definite integral from a to b using Simpson's 1/3 rule.
    """
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    
    try:
        s = expr.evaluate({var: a}) + expr.evaluate({var: b})
        for i in range(1, n):
            x_i = a + i * h
            val = expr.evaluate({var: x_i})
            s += 4 * val if i % 2 == 1 else 2 * val
        return (h / 3.0) * s
    except Exception:
        return float('nan')
