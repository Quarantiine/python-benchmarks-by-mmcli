"""
Symbolic Integration Engine
===========================
Implements symbolic indefinite integration (antiderivatives) and numerical/analytical
definite integration across polynomials, power rules, trigonometric, exponential,
logarithmic, rational, inverse trigonometric functions, and integration by parts.
"""

from __future__ import annotations
from fractions import Fraction
import math
from typing import Optional, Tuple, Union, List

from ast_nodes import (
    Node, Constant, Variable, NamedConstant,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Sec, Csc, Cot,
    Asin, Acos, Atan, Sinh, Cosh, Tanh,
    Exp, Ln, Log, Sqrt, Abs,
    E, PI, to_node
)
from simplifier import simplify, _is_num


def _eval_const_val(node: Node) -> Optional[Union[int, float, Fraction]]:
    """Extract numeric value if node is Constant, Negate(Constant), or simplifiable to constant."""
    if isinstance(node, Constant):
        return node.value
    if isinstance(node, Negate):
        inner = _eval_const_val(node.child)
        if inner is not None:
            return -inner
    if isinstance(node, Divide) and isinstance(node.left, Constant) and isinstance(node.right, Constant):
        if isinstance(node.left.value, int) and isinstance(node.right.value, int) and node.right.value != 0:
            return Fraction(node.left.value, node.right.value)
        elif node.right.value != 0:
            return node.left.value / node.right.value
    return None


def _linear_arg(node: Node, var: str) -> Optional[Tuple[Union[int, float, Fraction], Union[int, float, Fraction]]]:
    """
    Check if `node` is an affine linear expression of the form (a * var + b).
    Returns (a, b) if linear, or None otherwise.
    """
    if isinstance(node, Variable) and node.name == var:
        return (1, 0)
    if isinstance(node, Constant):
        return (0, node.value)

    if isinstance(node, Multiply):
        if isinstance(node.left, Constant) and isinstance(node.right, Variable) and node.right.name == var:
            return (node.left.value, 0)
        if isinstance(node.right, Constant) and isinstance(node.left, Variable) and node.left.name == var:
            return (node.right.value, 0)

    if isinstance(node, Add):
        if isinstance(node.left, Variable) and node.left.name == var and isinstance(node.right, Constant):
            return (1, node.right.value)
        if isinstance(node.right, Variable) and node.right.name == var and isinstance(node.left, Constant):
            return (1, node.left.value)
        if isinstance(node.left, Multiply) and isinstance(node.right, Constant):
            l_lin = _linear_arg(node.left, var)
            if l_lin and l_lin[1] == 0:
                return (l_lin[0], node.right.value)
        if isinstance(node.right, Multiply) and isinstance(node.left, Constant):
            r_lin = _linear_arg(node.right, var)
            if r_lin and r_lin[1] == 0:
                return (r_lin[0], node.left.value)

    if isinstance(node, Subtract):
        if isinstance(node.left, Variable) and node.left.name == var and isinstance(node.right, Constant):
            return (1, -node.right.value)
        if isinstance(node.left, Multiply) and isinstance(node.right, Constant):
            l_lin = _linear_arg(node.left, var)
            if l_lin and l_lin[1] == 0:
                return (l_lin[0], -node.right.value)

    if isinstance(node, Negate):
        inner = _linear_arg(node.child, var)
        if inner:
            return (-inner[0], -inner[1])

    return None


def _integrate_node(node: Node, var: str) -> Optional[Node]:
    """Internal recursive symbolic integrator."""
    v_node = Variable(var)

    # 1. Constant with respect to var
    if node.is_constant() or (isinstance(node, Variable) and node.name != var):
        return Multiply(node, v_node)

    # 2. Free variable x
    if isinstance(node, Variable) and node.name == var:
        # x^2 / 2
        return Divide(Power(v_node, Constant(2)), Constant(2))

    # 3. Negate
    if isinstance(node, Negate):
        inner = _integrate_node(node.child, var)
        return Negate(inner) if inner is not None else None

    # 4. Add / Subtract (Linearity)
    if isinstance(node, Add):
        left_int = _integrate_node(node.left, var)
        right_int = _integrate_node(node.right, var)
        if left_int is not None and right_int is not None:
            return Add(left_int, right_int)
        return None

    if isinstance(node, Subtract):
        left_int = _integrate_node(node.left, var)
        right_int = _integrate_node(node.right, var)
        if left_int is not None and right_int is not None:
            return Subtract(left_int, right_int)
        return None

    # 5. Constant Multiple: c * f(x) or f(x) * c
    if isinstance(node, Multiply):
        if node.left.is_constant():
            inner = _integrate_node(node.right, var)
            if inner is not None:
                return Multiply(node.left, inner)
        if node.right.is_constant():
            inner = _integrate_node(node.left, var)
            if inner is not None:
                return Multiply(node.right, inner)

        # Integration by parts:
        # x * exp(x) -> (x - 1) * exp(x)
        if isinstance(node.left, Variable) and node.left.name == var:
            # x * exp(a*x)
            if isinstance(node.right, Exp):
                lin = _linear_arg(node.right.child, var)
                if lin and lin[1] == 0 and lin[0] != 0:
                    a_val = lin[0]
                    # ∫ x * exp(a*x) dx = (a*x - 1)/a^2 * exp(a*x)
                    return Divide(
                        Multiply(Subtract(Multiply(Constant(a_val), v_node), Constant(1)), Exp(node.right.child)),
                        Constant(a_val * a_val)
                    )
            # x * sin(x) -> sin(x) - x * cos(x)
            if isinstance(node.right, Sin) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                return Subtract(Sin(v_node), Multiply(v_node, Cos(v_node)))
            # x * cos(x) -> cos(x) + x * sin(x)
            if isinstance(node.right, Cos) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                return Add(Cos(v_node), Multiply(v_node, Sin(v_node)))
            # x * ln(x) -> (x^2 / 2) * ln(x) - x^2 / 4
            if isinstance(node.right, Ln) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                return Subtract(
                    Multiply(Divide(Power(v_node, Constant(2)), Constant(2)), Ln(v_node)),
                    Divide(Power(v_node, Constant(2)), Constant(4))
                )

        # x^n * ln(x) -> (x^(n+1)/(n+1)) * ln(x) - x^(n+1)/(n+1)^2
        if isinstance(node.left, Power) and isinstance(node.left.left, Variable) and node.left.left.name == var and isinstance(node.left.right, Constant):
            n_val = node.left.right.value
            if isinstance(node.right, Ln) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                if n_val != -1:
                    n_plus_1 = n_val + 1
                    return Subtract(
                        Multiply(Divide(Power(v_node, Constant(n_plus_1)), Constant(n_plus_1)), Ln(v_node)),
                        Divide(Power(v_node, Constant(n_plus_1)), Constant(n_plus_1 * n_plus_1))
                    )

        # exp(x) * sin(x) -> exp(x)*(sin(x) - cos(x))/2
        if isinstance(node.left, Exp) and isinstance(node.left.child, Variable) and node.left.child.name == var:
            if isinstance(node.right, Sin) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                return Divide(Multiply(Exp(v_node), Subtract(Sin(v_node), Cos(v_node))), Constant(2))
            if isinstance(node.right, Cos) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                return Divide(Multiply(Exp(v_node), Add(Sin(v_node), Cos(v_node))), Constant(2))

    # 6. Division: f(x) / c or 1 / (a*x + b) or 1 / (1 + x^2) or 1 / sqrt(1 - x^2)
    if isinstance(node, Divide):
        if node.right.is_constant():
            inner = _integrate_node(node.left, var)
            if inner is not None:
                return Divide(inner, node.right)

        if node.left.is_constant():
            c_num = node.left.value
            lin = _linear_arg(node.right, var)
            if lin and lin[0] != 0:
                a_val, b_val = lin
                # ∫ c / (ax + b) dx = (c/a) * ln|ax + b|
                res = Multiply(Constant(Fraction(c_num, a_val) if isinstance(c_num, int) and isinstance(a_val, int) else (c_num / a_val)), Ln(Abs(node.right)))
                return res

            # 1 / (1 + x^2) -> atan(x)
            if isinstance(node.right, Add):
                if _is_num(node.right.left, 1) and isinstance(node.right.right, Power) and isinstance(node.right.right.left, Variable) and node.right.right.left.name == var and _is_num(node.right.right.right, 2):
                    return Multiply(node.left, Atan(v_node))
                if _is_num(node.right.right, 1) and isinstance(node.right.left, Power) and isinstance(node.right.left.left, Variable) and node.right.left.left.name == var and _is_num(node.right.left.right, 2):
                    return Multiply(node.left, Atan(v_node))

            # 1 / sqrt(1 - x^2) -> asin(x)
            if isinstance(node.right, Sqrt) and isinstance(node.right.child, Subtract):
                sub = node.right.child
                if _is_num(sub.left, 1) and isinstance(sub.right, Power) and isinstance(sub.right.left, Variable) and sub.right.left.name == var and _is_num(sub.right.right, 2):
                    return Multiply(node.left, Asin(v_node))

    # 7. Power rule: (ax + b)^n
    if isinstance(node, Power):
        lin = _linear_arg(node.left, var)
        n_val = _eval_const_val(node.right)
        if lin and lin[0] != 0 and n_val is not None:
            a_val, _ = lin
            if n_val == -1:
                # 1 / (ax + b) -> (1/a) * ln|ax + b|
                return Divide(Ln(Abs(node.left)), Constant(a_val))
            else:
                n_plus_1 = n_val + 1
                coeff = Fraction(1, a_val * n_plus_1) if isinstance(a_val, int) and isinstance(n_plus_1, int) else (1.0 / (a_val * n_plus_1))
                return Multiply(Constant(coeff), Power(node.left, Constant(n_plus_1)))

    # 8. Sqrt: sqrt(ax + b) = (ax + b)^(1/2)
    if isinstance(node, Sqrt):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            # ∫ (ax + b)^(1/2) dx = (2 / 3a) * (ax + b)^(3/2)
            coeff = Fraction(2, 3 * a_val) if isinstance(a_val, int) else (2.0 / (3 * a_val))
            return Multiply(Constant(coeff), Power(node.child, Constant(Fraction(3, 2))))

    # 9. Elementary functions with linear argument: f(ax + b)
    if isinstance(node, Sin):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Negate(Divide(Cos(node.child), Constant(a_val)))

    if isinstance(node, Cos):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Divide(Sin(node.child), Constant(a_val))

    if isinstance(node, Tan):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Negate(Divide(Ln(Abs(Cos(node.child))), Constant(a_val)))

    if isinstance(node, Sec):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Divide(Ln(Abs(Add(Sec(node.child), Tan(node.child)))), Constant(a_val))

    if isinstance(node, Sinh):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Divide(Cosh(node.child), Constant(a_val))

    if isinstance(node, Cosh):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Divide(Sinh(node.child), Constant(a_val))

    if isinstance(node, Tanh):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Divide(Ln(Cosh(node.child)), Constant(a_val))

    if isinstance(node, Exp):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            return Divide(Exp(node.child), Constant(a_val))

    if isinstance(node, Ln):
        lin = _linear_arg(node.child, var)
        if lin and lin[0] != 0:
            a_val, _ = lin
            # ∫ ln(ax+b) dx = ((ax+b)*ln(ax+b) - (ax+b)) / a
            u_term = node.child
            return Divide(Subtract(Multiply(u_term, Ln(u_term)), u_term), Constant(a_val))

    if isinstance(node, Asin):
        if isinstance(node.child, Variable) and node.child.name == var:
            return Add(Multiply(v_node, Asin(v_node)), Sqrt(Subtract(Constant(1), Power(v_node, Constant(2)))))

    if isinstance(node, Acos):
        if isinstance(node.child, Variable) and node.child.name == var:
            return Subtract(Multiply(v_node, Acos(v_node)), Sqrt(Subtract(Constant(1), Power(v_node, Constant(2)))))

    if isinstance(node, Atan):
        if isinstance(node.child, Variable) and node.child.name == var:
            return Subtract(
                Multiply(v_node, Atan(v_node)),
                Multiply(Constant(Fraction(1, 2)), Ln(Add(Constant(1), Power(v_node, Constant(2)))))
            )

    return None


def integrate(
    expr: Union[Node, str],
    var: str = "x",
    simplify_result: bool = True
) -> Node:
    """
    Compute the indefinite integral (antiderivative) ∫ f(x) dx symbolically.

    Raises:
        ValueError if symbolic antiderivative cannot be constructed with available rules.
    """
    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    res = _integrate_node(expr, var)
    if res is None:
        raise ValueError(f"No symbolic antiderivative rule found for: {expr.to_infix()}")

    return simplify(res) if simplify_result else res


def _adaptive_simpson(f, a: float, b: float, tol: float = 1e-8, max_depth: int = 25) -> float:
    """Adaptive Simpson's numerical quadrature for robust definite integration."""
    def _simpson(fa: float, fb: float, fc: float, a: float, b: float) -> float:
        return (b - a) / 6.0 * (fa + 4.0 * fc + fb)

    def _asr(a: float, b: float, tol: float, whole: float, fa: float, fb: float, fc: float, depth: int) -> float:
        c = (a + b) / 2.0
        d = (a + c) / 2.0
        e = (c + b) / 2.0
        fd = f(d)
        fe = f(e)
        left = _simpson(fa, fc, fd, a, c)
        right = _simpson(fc, fb, fe, c, b)
        delta = left + right - whole
        if depth <= 0 or abs(delta) <= 15.0 * tol:
            return left + right + delta / 15.0
        return (_asr(a, c, tol / 2.0, left, fa, fc, fd, depth - 1) +
                _asr(c, b, tol / 2.0, right, fc, fb, fe, depth - 1))

    c = (a + b) / 2.0
    fa = f(a)
    fb = f(b)
    fc = f(c)
    whole = _simpson(fa, fb, fc, a, b)
    return _asr(a, b, tol, whole, fa, fb, fc, max_depth)


def definite_integrate(
    expr: Union[Node, str],
    var: str = "x",
    lower: Optional[float] = None,
    upper: Optional[float] = None,
    method: str = "auto",
    a: Optional[float] = None,
    b: Optional[float] = None,
) -> float:
    """
    Compute the definite integral ∫_{lower}^{upper} f(x) dx.
    First attempts exact evaluation via the Fundamental Theorem of Calculus (F(b) - F(a)),
    falling back to high-accuracy Adaptive Simpson numerical quadrature if needed.
    """
    if lower is None:
        lower = a if a is not None else 0.0
    if upper is None:
        upper = b if b is not None else 1.0

    if isinstance(expr, str):
        from parser import parse_expr
        expr = parse_expr(expr)

    # If bounds are equal
    if lower == upper:
        return 0.0

    # 1. Fundamental Theorem of Calculus
    if method in ("auto", "symbolic"):
        try:
            anti = integrate(expr, var=var, simplify_result=True)
            f_b = anti.evaluate({var: float(upper)})
            f_a = anti.evaluate({var: float(lower)})
            if not (math.isnan(f_b) or math.isnan(f_a) or math.isinf(f_b) or math.isinf(f_a)):
                val = f_b - f_a
                return int(val) if float(val).is_integer() else round(val, 8)
        except Exception:
            if method == "symbolic":
                raise

    # 2. Adaptive Simpson Numerical Quadrature
    def f_eval(x: float) -> float:
        try:
            v = expr.evaluate({var: x})
            return 0.0 if (math.isnan(v) or math.isinf(v)) else v
        except Exception:
            return 0.0

    quad = _adaptive_simpson(f_eval, float(lower), float(upper))
    if math.isclose(quad, round(quad), abs_tol=1e-5):
        return int(round(quad))
    return round(quad, 8)
