"""
Symbolic Differentiation Engine.

Computes exact symbolic derivatives using product rule, quotient rule, power rule,
chain rule, trigonometric, exponential, and logarithmic differentiation rules.
"""

from typing import Union, Tuple
from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Asin, Acos, Atan, Exp, Ln, Sqrt, Abs
)
from calculus.simplify import simplify


def diff(expr: Expr, var: Union[str, Symbol], simplify_result: bool = True) -> Expr:
    """
    Compute symbolic derivative of expr with respect to var.
    
    :param expr: Symbolic AST expression.
    :param var: Name of variable or Symbol object to differentiate with respect to.
    :param simplify_result: Whether to simplify the resulting derivative.
    :return: Symbolic derivative AST.
    """
    var_name = var.name if isinstance(var, Symbol) else str(var)
    raw_derivative = _differentiate(expr, var_name)
    if simplify_result:
        return simplify(raw_derivative)
    return raw_derivative


def _differentiate(expr: Expr, var: str) -> Expr:
    if var not in expr.free_symbols():
        return Const(0)

    if isinstance(expr, Const):
        return Const(0)

    if isinstance(expr, Symbol):
        return Const(1) if expr.name == var else Const(0)

    if isinstance(expr, Neg):
        return Neg(_differentiate(expr.operand, var))

    if isinstance(expr, Add):
        return Add(_differentiate(expr.left, var), _differentiate(expr.right, var))

    if isinstance(expr, Sub):
        return Sub(_differentiate(expr.left, var), _differentiate(expr.right, var))

    if isinstance(expr, Mul):
        # Product Rule: (u * v)' = u' * v + u * v'
        u, v = expr.left, expr.right
        du = _differentiate(u, var)
        dv = _differentiate(v, var)
        return Add(Mul(du, v), Mul(u, dv))

    if isinstance(expr, Div):
        # Quotient Rule: (u / v)' = (u' * v - u * v') / (v ^ 2)
        u, v = expr.left, expr.right
        du = _differentiate(u, var)
        dv = _differentiate(v, var)
        return Div(Sub(Mul(du, v), Mul(u, dv)), Pow(v, Const(2)))

    if isinstance(expr, Pow):
        # u ^ v
        u, v = expr.left, expr.right
        u_has_var = var in u.free_symbols()
        v_has_var = var in v.free_symbols()

        if not u_has_var and not v_has_var:
            return Const(0)

        if u_has_var and not v_has_var:
            # Power rule: d/dx [u^c] = c * u^(c-1) * u'
            du = _differentiate(u, var)
            return Mul(Mul(v, Pow(u, Sub(v, Const(1)))), du)

        if not u_has_var and v_has_var:
            # Exponential rule: d/dx [a^v] = a^v * ln(a) * v'
            dv = _differentiate(v, var)
            return Mul(Mul(Pow(u, v), Ln(u)), dv)

        # General case: u^v = exp(v * ln(u))
        # d/dx [u^v] = u^v * (v' * ln(u) + v * u' / u)
        du = _differentiate(u, var)
        dv = _differentiate(v, var)
        term1 = Mul(dv, Ln(u))
        term2 = Div(Mul(v, du), u)
        return Mul(Pow(u, v), Add(term1, term2))

    if isinstance(expr, Sin):
        # d/dx sin(u) = cos(u) * u'
        u = expr.operand
        du = _differentiate(u, var)
        return Mul(Cos(u), du)

    if isinstance(expr, Cos):
        # d/dx cos(u) = -sin(u) * u'
        u = expr.operand
        du = _differentiate(u, var)
        return Mul(Neg(Sin(u)), du)

    if isinstance(expr, Tan):
        # d/dx tan(u) = (1 + tan(u)^2) * u' = u' / cos(u)^2
        u = expr.operand
        du = _differentiate(u, var)
        return Div(du, Pow(Cos(u), Const(2)))

    if isinstance(expr, Asin):
        # d/dx asin(u) = u' / sqrt(1 - u^2)
        u = expr.operand
        du = _differentiate(u, var)
        return Div(du, Sqrt(Sub(Const(1), Pow(u, Const(2)))))

    if isinstance(expr, Acos):
        # d/dx acos(u) = -u' / sqrt(1 - u^2)
        u = expr.operand
        du = _differentiate(u, var)
        return Div(Neg(du), Sqrt(Sub(Const(1), Pow(u, Const(2)))))

    if isinstance(expr, Atan):
        # d/dx atan(u) = u' / (1 + u^2)
        u = expr.operand
        du = _differentiate(u, var)
        return Div(du, Add(Const(1), Pow(u, Const(2))))

    if isinstance(expr, Exp):
        # d/dx exp(u) = exp(u) * u'
        u = expr.operand
        du = _differentiate(u, var)
        return Mul(Exp(u), du)

    if isinstance(expr, Ln):
        # d/dx ln(u) = u' / u
        u = expr.operand
        du = _differentiate(u, var)
        return Div(du, u)

    if isinstance(expr, Sqrt):
        # d/dx sqrt(u) = u' / (2 * sqrt(u))
        u = expr.operand
        du = _differentiate(u, var)
        return Div(du, Mul(Const(2), Sqrt(u)))

    if isinstance(expr, Abs):
        # d/dx |u| = (u / |u|) * u'
        u = expr.operand
        du = _differentiate(u, var)
        return Mul(Div(u, Abs(u)), du)

    raise NotImplementedError(f"Differentiation rule for {type(expr).__name__} not implemented.")
