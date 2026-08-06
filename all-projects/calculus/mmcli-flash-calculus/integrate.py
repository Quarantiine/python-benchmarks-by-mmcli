"""
Symbolic Integration Engine.

Computes indefinite integrals and definite integrals (via Fundamental Theorem of Calculus
or adaptive quadrature fallback when requested) supporting polynomial powers,
exponential, trigonometric, logarithmic, and linear substitution patterns.
"""

import math
from typing import Optional, Union, Tuple
from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Exp, Ln, Sqrt, Abs
)
from calculus.simplify import simplify


def integrate(
    expr: Expr,
    var: Union[str, Symbol],
    lower: Optional[Union[float, int, Expr]] = None,
    upper: Optional[Union[float, int, Expr]] = None,
    simplify_result: bool = True
) -> Union[Expr, float]:
    """
    Compute indefinite or definite integral of expr with respect to var.

    :param expr: Symbolic expression AST.
    :param var: Integration variable.
    :param lower: Optional lower bound for definite integration.
    :param upper: Optional upper bound for definite integration.
    :param simplify_result: Whether to simplify the resulting expression.
    :return: Indefinite integral AST or scalar float value for definite integral.
    """
    var_name = var.name if isinstance(var, Symbol) else str(var)
    expr = simplify(expr)
    indef_integral = _integrate_indefinite(expr, var_name)

    if simplify_result:
        indef_integral = simplify(indef_integral)

    if lower is None and upper is None:
        return indef_integral

    if lower is None or upper is None:
        raise ValueError("Both lower and upper bounds must be provided for definite integration.")

    # Definite integral F(upper) - F(lower)
    lower_expr = lower if isinstance(lower, Expr) else Const(lower)
    upper_expr = upper if isinstance(upper, Expr) else Const(upper)

    f_upper = indef_integral.subs(var_name, upper_expr)
    f_lower = indef_integral.subs(var_name, lower_expr)

    diff_expr = simplify(Sub(f_upper, f_lower))

    # Try numerical evaluation if bounds are numeric
    try:
        return diff_expr.eval()
    except (ValueError, TypeError, ZeroDivisionError):
        return diff_expr


def _integrate_indefinite(expr: Expr, var: str) -> Expr:
    expr = simplify(expr)

    # 1. Independent of variable -> c * x
    if var not in expr.free_symbols():
        return Mul(expr, Symbol(var))

    # 2. Variable itself -> x^2 / 2
    if isinstance(expr, Symbol) and expr.name == var:
        return Div(Pow(Symbol(var), Const(2)), Const(2))

    # 3. Addition / Subtraction (linearity)
    if isinstance(expr, Add):
        return Add(_integrate_indefinite(expr.left, var), _integrate_indefinite(expr.right, var))

    if isinstance(expr, Sub):
        return Sub(_integrate_indefinite(expr.left, var), _integrate_indefinite(expr.right, var))

    # 4. Negation
    if isinstance(expr, Neg):
        return Neg(_integrate_indefinite(expr.operand, var))

    # 5. Multiplication by constant factor
    if isinstance(expr, Mul):
        left_has = var in expr.left.free_symbols()
        right_has = var in expr.right.free_symbols()

        if not left_has:
            return Mul(expr.left, _integrate_indefinite(expr.right, var))
        if not right_has:
            return Mul(expr.right, _integrate_indefinite(expr.left, var))

        # Check for x * e^(a*x) or x * sin(a*x) or x * cos(a*x) (Integration by Parts)
        ibp_result = _try_integration_by_parts(expr, var)
        if ibp_result is not None:
            return ibp_result

    # 6. Power rule: x^n or (a*x + b)^n
    if isinstance(expr, Pow):
        base, exp = expr.left, expr.right
        if var in base.free_symbols() and var not in exp.free_symbols():
            # Check linear base: a*x + b
            a, b = _extract_linear_coefs(base, var)
            if a is not None:
                # integral of (a*x + b)^n dx = (a*x + b)^(n+1) / (a * (n+1))
                if exp == Const(-1) or exp == Neg(Const(1)):
                    return Div(Ln(Abs(base)), Const(a))
                else:
                    new_exp = Add(exp, Const(1))
                    denom = Mul(Const(a), new_exp)
                    return Div(Pow(base, new_exp), denom)

        if var not in base.free_symbols() and var in exp.free_symbols():
            # Exponential: a^(k*x + b)
            k, b = _extract_linear_coefs(exp, var)
            if k is not None:
                # integral of a^(k*x + b) dx = a^(k*x + b) / (k * ln(a))
                denom = Mul(Const(k), Ln(base))
                return Div(expr, denom)

    # 7. Trigonometric functions
    if isinstance(expr, Sin):
        a, b = _extract_linear_coefs(expr.operand, var)
        if a is not None:
            # integral sin(a*x + b) dx = -cos(a*x + b) / a
            return Div(Neg(Cos(expr.operand)), Const(a))

    if isinstance(expr, Cos):
        a, b = _extract_linear_coefs(expr.operand, var)
        if a is not None:
            # integral cos(a*x + b) dx = sin(a*x + b) / a
            return Div(Sin(expr.operand), Const(a))

    # 8. Exponential e^(a*x + b)
    if isinstance(expr, Exp):
        a, b = _extract_linear_coefs(expr.operand, var)
        if a is not None:
            # integral exp(a*x + b) dx = exp(a*x + b) / a
            return Div(expr, Const(a))

    # 9. Natural log ln(a*x + b)
    if isinstance(expr, Ln):
        a, b = _extract_linear_coefs(expr.operand, var)
        if a is not None:
            # integral ln(u) dx = (u * ln(u) - u) / a
            u = expr.operand
            num = Sub(Mul(u, Ln(u)), u)
            return Div(num, Const(a))

    # 10. Division (e.g. f(x) / c or 1 / (a*x + b) or c / (a*x + b)^n)
    if isinstance(expr, Div):
        left, right = expr.left, expr.right
        if var not in right.free_symbols():
            return Div(_integrate_indefinite(left, var), right)
        if var not in left.free_symbols() and var in right.free_symbols():
            a, b = _extract_linear_coefs(right, var)
            if a is not None:
                # integral c / (a*x + b) dx = (c/a) * ln(|a*x + b|)
                return Mul(Div(left, Const(a)), Ln(Abs(right)))

            if isinstance(right, Pow):
                base, exp = right.left, right.right
                if var in base.free_symbols() and var not in exp.free_symbols():
                    a, b = _extract_linear_coefs(base, var)
                    if a is not None:
                        try:
                            exp_val = exp.eval()
                            if exp_val == 1:
                                return Mul(Div(left, Const(a)), Ln(Abs(base)))
                            new_exp = Sub(Const(1), exp)
                            denom = Mul(Const(a), new_exp)
                            return Div(Mul(left, Pow(base, new_exp)), denom)
                        except Exception:
                            pass

    raise NotImplementedError(f"Integration rule for expression '{expr}' with variable '{var}' is not supported.")


def _get_linear_coefs_raw(expr: Expr, var: str) -> Tuple[Optional[float], Optional[float]]:
    """Recursively calculate linear form a*x + b for sub-expressions."""
    expr = simplify(expr)
    if isinstance(expr, Const) and var not in expr.free_symbols():
        return (0.0, float(expr.value))
    if isinstance(expr, Symbol) and expr.name == var:
        return (1.0, 0.0)
    if isinstance(expr, Neg):
        a, b = _get_linear_coefs_raw(expr.operand, var)
        if a is not None and b is not None:
            return (-a, -b)
    if isinstance(expr, Mul):
        if isinstance(expr.left, Const) and isinstance(expr.right, Symbol) and expr.right.name == var:
            return (float(expr.left.value), 0.0)
        if isinstance(expr.right, Const) and isinstance(expr.left, Symbol) and expr.left.name == var:
            return (float(expr.right.value), 0.0)
    if isinstance(expr, Add):
        a1, b1 = _get_linear_coefs_raw(expr.left, var)
        a2, b2 = _get_linear_coefs_raw(expr.right, var)
        if a1 is not None and a2 is not None and b1 is not None and b2 is not None:
            return (a1 + a2, b1 + b2)
    if isinstance(expr, Sub):
        a1, b1 = _get_linear_coefs_raw(expr.left, var)
        a2, b2 = _get_linear_coefs_raw(expr.right, var)
        if a1 is not None and a2 is not None and b1 is not None and b2 is not None:
            return (a1 - a2, b1 - b2)
    return (None, None)


def _extract_linear_coefs(expr: Expr, var: str) -> Tuple[Optional[float], Optional[float]]:
    """Check if expr is linear in var (a*x + b with a != 0) and return coefficients (a, b)."""
    a, b = _get_linear_coefs_raw(expr, var)
    if a is not None and a != 0:
        return (a, b)
    return (None, None)


def _try_integration_by_parts(expr: Mul, var: str) -> Optional[Expr]:
    """Helper for basic integration by parts: integral u dv = u v - integral v du."""
    left, right = expr.left, expr.right
    # Check if x * e^(a*x) or x * sin(a*x) or x * cos(a*x)
    if isinstance(left, Symbol) and left.name == var:
        u = left
        dv = right
    elif isinstance(right, Symbol) and right.name == var:
        u = right
        dv = left
    else:
        return None

    try:
        v = _integrate_indefinite(dv, var)
        du = Const(1)  # d/dx[x] = 1
        # integral u dv = u * v - integral (v * du)
        v_du = Mul(v, du)
        integral_v_du = _integrate_indefinite(v_du, var)
        return Sub(Mul(u, v), integral_v_du)
    except NotImplementedError:
        return None
