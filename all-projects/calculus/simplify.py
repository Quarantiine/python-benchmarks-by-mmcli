"""
Symbolic Expression Simplifier.

Applies algebraic identities, constant folding, term combining,
trigonometric and exponential simplifications repeatedly until fixpoint.
"""

import math
from typing import Tuple, Union
from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Exp, Ln, Sqrt, Abs, E_CONST, PI_CONST
)


def simplify(expr: Expr, max_passes: int = 10) -> Expr:
    """Recursively simplify an expression until no further rules apply or max_passes is reached."""
    current = expr
    for _ in range(max_passes):
        simplified = _simplify_step(current)
        if simplified == current:
            break
        current = simplified
    return current


def _simplify_step(expr: Expr) -> Expr:
    if isinstance(expr, (Const, Symbol)):
        return expr

    if isinstance(expr, Neg):
        sub = _simplify_step(expr.operand)
        if isinstance(sub, Const):
            return Const(-sub.value)
        if isinstance(sub, Neg):
            return sub.operand
        return Neg(sub)

    if isinstance(expr, Add):
        left = _simplify_step(expr.left)
        right = _simplify_step(expr.right)

        # Constant folding
        if isinstance(left, Const) and isinstance(right, Const):
            return Const(left.value + right.value)

        # Add zero identity
        if isinstance(left, Const) and left.value == 0:
            return right
        if isinstance(right, Const) and right.value == 0:
            return left

        # Combine identical terms: x + x -> 2*x
        if left == right:
            return Mul(Const(2), left)

        # x + (-y) -> x - y, (-x) + y -> y - x
        if isinstance(right, Neg):
            return Sub(left, right.operand)
        if isinstance(left, Neg):
            return Sub(right, left.operand)

        # Combine like linear terms: c1*x + c2*x -> (c1+c2)*x
        c1, term1 = _extract_coef_term(left)
        c2, term2 = _extract_coef_term(right)
        if term1 == term2:
            new_c = c1 + c2
            if new_c == 0:
                return Const(0)
            if new_c == 1:
                return term1
            return Mul(Const(new_c), term1)

        # Ordering constants to the right for canonical form
        if isinstance(left, Const) and not isinstance(right, Const):
            return Add(right, left)

        return Add(left, right)

    if isinstance(expr, Sub):
        left = _simplify_step(expr.left)
        right = _simplify_step(expr.right)

        # Constant folding
        if isinstance(left, Const) and isinstance(right, Const):
            return Const(left.value - right.value)

        # Sub zero identity
        if isinstance(right, Const) and right.value == 0:
            return left
        if isinstance(left, Const) and left.value == 0:
            if isinstance(right, Neg):
                return right.operand
            return Neg(right)

        # x - x -> 0
        if left == right:
            return Const(0)

        # x - (-y) -> x + y
        if isinstance(right, Neg):
            return Add(left, right.operand)

        # Combine like linear terms: c1*x - c2*x -> (c1-c2)*x
        c1, term1 = _extract_coef_term(left)
        c2, term2 = _extract_coef_term(right)
        if term1 == term2:
            new_c = c1 - c2
            if new_c == 0:
                return Const(0)
            if new_c == 1:
                return term1
            return Mul(Const(new_c), term1)

        return Sub(left, right)

    if isinstance(expr, Mul):
        left = _simplify_step(expr.left)
        right = _simplify_step(expr.right)

        # Constant folding
        if isinstance(left, Const) and isinstance(right, Const):
            return Const(left.value * right.value)

        # Zero property: 0 * x -> 0, x * 0 -> 0
        if (isinstance(left, Const) and left.value == 0) or (isinstance(right, Const) and right.value == 0):
            return Const(0)

        # One property: 1 * x -> x, x * 1 -> x
        if isinstance(left, Const) and left.value == 1:
            return right
        if isinstance(right, Const) and right.value == 1:
            return left

        # Neg one property: -1 * x -> -x
        if isinstance(left, Const) and left.value == -1:
            return Neg(right)
        if isinstance(right, Const) and right.value == -1:
            return Neg(left)

        # Negation handling: (-x) * y -> -(x * y), (-x) * (-y) -> x * y
        if isinstance(left, Neg) and isinstance(right, Neg):
            return Mul(left.operand, right.operand)
        if isinstance(left, Neg):
            return Neg(Mul(left.operand, right))
        if isinstance(right, Neg):
            return Neg(Mul(left, right.operand))

        # Power combination: x^a * x^b -> x^(a+b), x * x^a -> x^(a+1), x * x -> x^2
        b1, e1 = _extract_base_exp(left)
        b2, e2 = _extract_base_exp(right)
        if b1 == b2:
            return Pow(b1, Add(e1, e2))

        # Associative constant gathering: c1 * (c2 * x) -> (c1*c2) * x
        if isinstance(left, Const) and isinstance(right, Mul) and isinstance(right.left, Const):
            return Mul(Const(left.value * right.left.value), right.right)

        # Move constant coefficient to left: x * c -> c * x
        if isinstance(right, Const) and not isinstance(left, Const):
            return Mul(right, left)

        return Mul(left, right)

    if isinstance(expr, Div):
        left = _simplify_step(expr.left)
        right = _simplify_step(expr.right)

        # Constant folding
        if isinstance(left, Const) and isinstance(right, Const):
            if right.value == 0:
                raise ZeroDivisionError("Division by zero in simplification.")
            val = left.value / right.value
            if val.is_integer():
                return Const(int(val))
            return Const(val)

        # 0 / x -> 0
        if isinstance(left, Const) and left.value == 0:
            return Const(0)

        # x / 1 -> x
        if isinstance(right, Const) and right.value == 1:
            return left

        # x / x -> 1
        if left == right:
            return Const(1)

        # x / (-1) -> -x
        if isinstance(right, Const) and right.value == -1:
            return Neg(left)

        # (-x) / y or x / (-y) -> -(x / y)
        if isinstance(left, Neg) and isinstance(right, Neg):
            return Div(left.operand, right.operand)
        if isinstance(left, Neg):
            return Neg(Div(left.operand, right))
        if isinstance(right, Neg):
            return Neg(Div(left, right.operand))

        # Power division: x^a / x^b -> x^(a-b)
        b1, e1 = _extract_base_exp(left)
        b2, e2 = _extract_base_exp(right)
        if b1 == b2:
            return Pow(b1, Sub(e1, e2))

        return Div(left, right)

    if isinstance(expr, Pow):
        base = _simplify_step(expr.left)
        exp = _simplify_step(expr.right)

        # Constant folding
        if isinstance(base, Const) and isinstance(exp, Const):
            return Const(base.value ** exp.value)

        # x ^ 0 -> 1
        if isinstance(exp, Const) and exp.value == 0:
            return Const(1)

        # x ^ 1 -> x
        if isinstance(exp, Const) and exp.value == 1:
            return base

        # 1 ^ x -> 1
        if isinstance(base, Const) and base.value == 1:
            return Const(1)

        # 0 ^ x -> 0
        if isinstance(base, Const) and base.value == 0:
            return Const(0)

        # (x ^ a) ^ b -> x ^ (a * b)
        if isinstance(base, Pow):
            return Pow(base.left, Mul(base.right, exp))

        # e ^ ln(x) -> x
        if base == E_CONST or (isinstance(base, Symbol) and base.name == "e"):
            if isinstance(exp, Ln):
                return exp.operand

        return Pow(base, exp)

    if isinstance(expr, Sin):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const) and arg.value == 0:
            return Const(0)
        if isinstance(arg, Neg):
            return Neg(Sin(arg.operand))
        return Sin(arg)

    if isinstance(expr, Cos):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const) and arg.value == 0:
            return Const(1)
        if isinstance(arg, Neg):
            return Cos(arg.operand)
        return Cos(arg)

    if isinstance(expr, Tan):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const) and arg.value == 0:
            return Const(0)
        return Tan(arg)

    if isinstance(expr, Exp):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const) and arg.value == 0:
            return Const(1)
        if isinstance(arg, Ln):
            return arg.operand
        return Exp(arg)

    if isinstance(expr, Ln):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const) and arg.value == 1:
            return Const(0)
        if arg == E_CONST or (isinstance(arg, Symbol) and arg.name == "e"):
            return Const(1)
        if isinstance(arg, Exp):
            return arg.operand
        return Ln(arg)

    if isinstance(expr, Sqrt):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const):
            if arg.value == 0:
                return Const(0)
            if arg.value == 1:
                return Const(1)
            sq = math.isqrt(int(arg.value)) if arg.value >= 0 and arg.value.is_integer() else None
            if sq is not None and sq * sq == int(arg.value):
                return Const(sq)
        if isinstance(arg, Pow) and isinstance(arg.right, Const) and arg.right.value == 2:
            return Abs(arg.left)
        return Sqrt(arg)

    if isinstance(expr, Abs):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const):
            return Const(abs(arg.value))
        if isinstance(arg, Neg):
            return Abs(arg.operand)
        return Abs(arg)

    return expr


def _extract_coef_term(expr: Expr) -> Tuple[float, Expr]:
    """Helper to split c * term into numeric coefficient c and symbolic term."""
    if isinstance(expr, Const):
        return (expr.value, Const(1))
    if isinstance(expr, Mul):
        if isinstance(expr.left, Const):
            return (expr.left.value, expr.right)
        if isinstance(expr.right, Const):
            return (expr.right.value, expr.left)
    if isinstance(expr, Neg):
        c, term = _extract_coef_term(expr.operand)
        return (-c, term)
    return (1.0, expr)


def _extract_base_exp(expr: Expr) -> Tuple[Expr, Expr]:
    """Helper to split base ^ exp or treat expression as expr ^ 1."""
    if isinstance(expr, Pow):
        return (expr.left, expr.right)
    return (expr, Const(1))
