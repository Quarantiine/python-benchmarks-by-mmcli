"""
Symbolic Integration Engine
===========================
Implements symbolic indefinite integration (antiderivatives) and definite integration.
"""

from __future__ import annotations
from fractions import Fraction
from typing import Optional, Union, Tuple
from .ast_nodes import (
    Node, Constant, Variable, NamedConstant,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Sec, Csc, Cot,
    Asin, Acos, Atan, Sinh, Cosh, Tanh,
    Exp, Ln, Log, Sqrt, Abs,
    E, PI, _to_node
)
from .simplifier import simplify, _is_num


def _linear_arg(node: Node, var: str) -> Optional[Tuple[Union[int, float, Fraction], Union[int, float, Fraction]]]:
    """Check if node is of the form (a * var + b) and return (a, b)."""
    if isinstance(node, Variable) and node.name == var:
        return (1, 0)
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
    return None


def _symbolic_integrate_node(node: Node, var: str) -> Optional[Node]:
    v_node = Variable(var)

    # 1. Constant
    if node.is_constant() or (isinstance(node, Variable) and node.name != var):
        return Multiply(node, v_node)

    # 2. Variable x
    if isinstance(node, Variable) and node.name == var:
        # x^2 / 2
        return Divide(Power(v_node, Constant(2)), Constant(2))

    # 3. Negate
    if isinstance(node, Negate):
        inner = _symbolic_integrate_node(node.child, var)
        return Negate(inner) if inner is not None else None

    # 4. Add / Subtract (Linearity)
    if isinstance(node, Add):
        left_int = _symbolic_integrate_node(node.left, var)
        right_int = _symbolic_integrate_node(node.right, var)
        if left_int is not None and right_int is not None:
            return Add(left_int, right_int)
        return None

    if isinstance(node, Subtract):
        left_int = _symbolic_integrate_node(node.left, var)
        right_int = _symbolic_integrate_node(node.right, var)
        if left_int is not None and right_int is not None:
            return Subtract(left_int, right_int)
        return None

    # 5. Constant Multiple: c * f(x) or f(x) * c
    if isinstance(node, Multiply):
        if node.left.is_constant():
            inner = _symbolic_integrate_node(node.right, var)
            if inner is not None:
                return Multiply(node.left, inner)
        if node.right.is_constant():
            inner = _symbolic_integrate_node(node.left, var)
            if inner is not None:
                return Multiply(node.right, inner)

        # Integration by parts: x * exp(x), x * sin(x), x * cos(x), x * ln(x)
        if isinstance(node.left, Variable) and node.left.name == var:
            if isinstance(node.right, Exp) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                # x * exp(x) -> (x - 1) * exp(x)
                return Multiply(Subtract(v_node, Constant(1)), Exp(v_node))
            if isinstance(node.right, Sin) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                # x * sin(x) -> sin(x) - x * cos(x)
                return Subtract(Sin(v_node), Multiply(v_node, Cos(v_node)))
            if isinstance(node.right, Cos) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                # x * cos(x) -> cos(x) + x * sin(x)
                return Add(Cos(v_node), Multiply(v_node, Sin(v_node)))
            if isinstance(node.right, Ln) and isinstance(node.right.child, Variable) and node.right.child.name == var:
                # x * ln(x) -> (x^2 / 2) * ln(x) - x^2 / 4
                return Subtract(
                    Multiply(Divide(Power(v_node, Constant(2)), Constant(2)), Ln(v_node)),
                    Divide(Power(v_node, Constant(2)), Constant(4))
                )

    # 6. Division: f(x) / c or 1 / (ax + b) or 1 / x
    if isinstance(node, Divide):
        if node.right.is_constant():
            inner = _symbolic_integrate_node(node.left, var)
            if inner is not None:
                return Divide(inner, node.right)

        if _is_num(node.left, 1):
            if isinstance(node.right, Variable) and node.right.name == var:
                # 1 / x -> ln(x)
                return Ln(v_node)

            lin = _linear_arg(node.right, var)
            if lin:
                a, b = lin
                if a != 0:
                    # 1 / (ax + b) -> ln(ax + b) / a
                    return Divide(Ln(node.right), Constant(a))

            # 1 / (1 + x^2) -> atan(x)
            if isinstance(node.right, Add):
                if (_is_num(node.right.left, 1) and isinstance(node.right.right, Power)
                        and isinstance(node.right.right.left, Variable) and node.right.right.left.name == var
                        and _is_num(node.right.right.right, 2)):
                    return Atan(v_node)

    # 7. Powers: (a*x + b)^n
    if isinstance(node, Power):
        base, exp = node.left, node.right
        if exp.is_constant():
            if isinstance(exp, Constant):
                n_val = exp.value
            else:
                n_val = None

            lin = _linear_arg(base, var)
            if lin:
                a, b = lin
                if n_val == -1:
                    return Divide(Ln(base), Constant(a)) if a != 1 else Ln(base)
                if n_val is not None and n_val != -1:
                    new_exp = n_val + 1
                    coeff = a * new_exp
                    numerator = Power(base, Constant(new_exp))
                    return Divide(numerator, Constant(coeff))

    # 8. Elementary Functions with linear arguments
    if isinstance(node, Sin):
        lin = _linear_arg(node.child, var)
        if lin:
            a, _ = lin
            # -cos(u) / a
            return Divide(Negate(Cos(node.child)), Constant(a))

    if isinstance(node, Cos):
        lin = _linear_arg(node.child, var)
        if lin:
            a, _ = lin
            # sin(u) / a
            return Divide(Sin(node.child), Constant(a))

    if isinstance(node, Exp):
        lin = _linear_arg(node.child, var)
        if lin:
            a, _ = lin
            # exp(u) / a
            return Divide(Exp(node.child), Constant(a))

    if isinstance(node, Ln) and isinstance(node.child, Variable) and node.child.name == var:
        # ln(x) -> x*ln(x) - x
        return Subtract(Multiply(v_node, Ln(v_node)), v_node)

    if isinstance(node, Sqrt):
        lin = _linear_arg(node.child, var)
        if lin:
            a, _ = lin
            # sqrt(ax + b) = (ax + b)^(1/2) -> (2/3a) * (ax + b)^(3/2)
            coeff = Fraction(2, 3 * a) if isinstance(a, int) else 2 / (3 * a)
            return Multiply(Constant(coeff), Power(node.child, Constant(Fraction(3, 2))))

    return None


def integrate(expr: Union[Node, str], var: str = "x") -> Node:
    """Compute the symbolic indefinite integral (antiderivative) of expr with respect to var."""
    if isinstance(expr, str):
        from .parser import parse_expr
        expr = parse_expr(expr)

    res = _symbolic_integrate_node(expr, var)
    if res is None:
        raise NotImplementedError(f"Symbolic indefinite integration not supported for '{expr.to_infix()}'")
    return simplify(res)


def definite_integrate(
    expr: Union[Node, str],
    var: str = "x",
    lower: float = 0.0,
    upper: float = 1.0
) -> float:
    """Compute the definite integral from lower to upper (analytical with Simpson fallback)."""
    if isinstance(expr, str):
        from .parser import parse_expr
        expr = parse_expr(expr)

    try:
        anti = integrate(expr, var)
        val_hi = anti.evaluate({var: upper})
        val_lo = anti.evaluate({var: lower})
        return float(val_hi - val_lo)
    except Exception:
        from .differentiator import definite_integral_approx
        return definite_integral_approx(expr, var=var, a=lower, b=upper)
