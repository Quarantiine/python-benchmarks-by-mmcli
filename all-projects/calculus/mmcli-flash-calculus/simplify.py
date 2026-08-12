"""
Symbolic Expression Simplifier.

Applies algebraic identities, constant folding, term combining,
trigonometric and exponential simplifications repeatedly until fixpoint.
"""

import math
from typing import Tuple, Union
from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Asin, Acos, Atan, Exp, Ln, Sqrt, Abs, E_CONST, PI_CONST
)


def _make_const(val: Union[int, float, complex]) -> Const:
    """Safely construct a Const, cleaning complex components and floating integer representations."""
    if isinstance(val, complex):
        r = val.real
        i = val.imag
        if abs(r) < 1e-15:
            r = 0.0
        if abs(i) < 1e-15:
            i = 0.0
        if i == 0.0:
            val = r
        else:
            val = complex(r, i)
    if isinstance(val, float) and val.is_integer():
        return Const(int(val))
    return Const(val)


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
            return _make_const(-sub.value)
        if isinstance(sub, Neg):
            return sub.operand
        return Neg(sub)

    if isinstance(expr, Add):
        left = _simplify_step(expr.left)
        right = _simplify_step(expr.right)

        # Constant folding
        if isinstance(left, Const) and isinstance(right, Const):
            return _make_const(left.value + right.value)

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
            return Mul(_make_const(new_c), term1)

        # Associative constant gathering for addition
        if isinstance(right, Const):
            if isinstance(left, Add) and isinstance(left.right, Const):
                return Add(left.left, _make_const(left.right.value + right.value))
            if isinstance(left, Add) and isinstance(left.left, Const):
                return Add(left.right, _make_const(left.left.value + right.value))
            if isinstance(left, Sub) and isinstance(left.right, Const):
                return Add(left.left, _make_const(right.value - left.right.value))
            if isinstance(left, Sub) and isinstance(left.left, Const):
                return Sub(_make_const(left.left.value + right.value), left.right)

        if isinstance(left, Const):
            if isinstance(right, Add) and isinstance(right.right, Const):
                return Add(right.left, _make_const(left.value + right.right.value))
            if isinstance(right, Add) and isinstance(right.left, Const):
                return Add(right.right, _make_const(left.value + right.left.value))
            if isinstance(right, Sub) and isinstance(right.right, Const):
                return Add(right.left, _make_const(left.value - right.right.value))

        # Ordering constants to the right for canonical form
        if isinstance(left, Const) and not isinstance(right, Const):
            return Add(right, left)

        return Add(left, right)

    if isinstance(expr, Sub):
        left = _simplify_step(expr.left)
        right = _simplify_step(expr.right)

        # Constant folding
        if isinstance(left, Const) and isinstance(right, Const):
            return _make_const(left.value - right.value)

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
            return Mul(_make_const(new_c), term1)

        # Associative constant gathering for subtraction
        if isinstance(right, Const):
            if isinstance(left, Add) and isinstance(left.right, Const):
                return Add(left.left, _make_const(left.right.value - right.value))
            if isinstance(left, Add) and isinstance(left.left, Const):
                return Add(left.right, _make_const(left.left.value - right.value))
            if isinstance(left, Sub) and isinstance(left.right, Const):
                return Sub(left.left, _make_const(left.right.value + right.value))
            if isinstance(left, Sub) and isinstance(left.left, Const):
                return Sub(_make_const(left.left.value - right.value), left.right)

        if isinstance(left, Const):
            if isinstance(right, Add) and isinstance(right.right, Const):
                return Sub(_make_const(left.value - right.right.value), right.left)
            if isinstance(right, Add) and isinstance(right.left, Const):
                return Sub(_make_const(left.value - right.left.value), right.right)
            if isinstance(right, Sub) and isinstance(right.right, Const):
                return Sub(_make_const(left.value + right.right.value), right.left)

        return Sub(left, right)

    if isinstance(expr, Mul):
        left = _simplify_step(expr.left)
        right = _simplify_step(expr.right)

        # Constant folding
        if isinstance(left, Const) and isinstance(right, Const):
            return _make_const(left.value * right.value)

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
        if isinstance(right, Const):
            if isinstance(left, Mul) and isinstance(left.right, Const):
                return Mul(_make_const(left.right.value * right.value), left.left)
            if isinstance(left, Mul) and isinstance(left.left, Const):
                return Mul(_make_const(left.left.value * right.value), left.right)

        if isinstance(left, Const):
            if isinstance(right, Mul) and isinstance(right.right, Const):
                return Mul(_make_const(left.value * right.right.value), right.left)
            if isinstance(right, Mul) and isinstance(right.left, Const):
                return Mul(_make_const(left.value * right.left.value), right.right)

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
            return _make_const(left.value / right.value)

        # 0 / x -> 0
        if isinstance(left, Const) and left.value == 0:
            return Const(0)

        # x / 1 -> x
        if isinstance(right, Const) and right.value == 1:
            return left

        # x / x -> 1
        if left == right:
            return Const(1)

        # Negative numerator constant: (-c) / x -> -(c / x)
        if isinstance(left, Const) and isinstance(left.value, (int, float)) and left.value < 0:
            return Neg(Div(_make_const(-left.value), right))

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
            if base.value == 0 and isinstance(exp.value, (int, float, complex)) and (isinstance(exp.value, complex) or exp.value < 0):
                raise ZeroDivisionError("Division by zero in simplification.")
            try:
                res = base.value ** exp.value
                return _make_const(res)
            except ZeroDivisionError:
                raise ZeroDivisionError("Division by zero in simplification.")
            except ArithmeticError:
                return Pow(base, exp)

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

    if isinstance(expr, Asin):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const):
            if arg.value == 0:
                return Const(0)
            if arg.value == 1:
                return Div(PI_CONST, Const(2))
            if arg.value == -1:
                return Neg(Div(PI_CONST, Const(2)))
        if isinstance(arg, Neg):
            return Neg(Asin(arg.operand))
        if isinstance(arg, Sin):
            return arg.operand
        return Asin(arg)

    if isinstance(expr, Acos):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const):
            if arg.value == 1:
                return Const(0)
            if arg.value == 0:
                return Div(PI_CONST, Const(2))
            if arg.value == -1:
                return PI_CONST
        if isinstance(arg, Cos):
            return arg.operand
        return Acos(arg)

    if isinstance(expr, Atan):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const):
            if arg.value == 0:
                return Const(0)
            if arg.value == 1:
                return Div(PI_CONST, Const(4))
            if arg.value == -1:
                return Neg(Div(PI_CONST, Const(4)))
        if isinstance(arg, Neg):
            return Neg(Atan(arg.operand))
        if isinstance(arg, Tan):
            return arg.operand
        return Atan(arg)

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
        if isinstance(arg, Pow):
            if arg.left == E_CONST or (isinstance(arg.left, Symbol) and arg.left.name == "e"):
                return arg.right
            return Mul(arg.right, Ln(arg.left))
        return Ln(arg)

    if isinstance(expr, Sqrt):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const):
            v = arg.value
            if isinstance(v, complex):
                if abs(v.imag) < 1e-15:
                    v = v.real
                else:
                    return Sqrt(arg)
            if isinstance(v, (int, float)):
                if v == 0:
                    return Const(0)
                if v == 1:
                    return Const(1)
                if v > 0:
                    root = math.sqrt(v)
                    if root.is_integer():
                        return Const(int(root))
                    elif root * root == v:
                        return Const(root)
        if isinstance(arg, Pow) and isinstance(arg.right, Const) and arg.right.value == 2:
            return Abs(arg.left)
        return Sqrt(arg)

    if isinstance(expr, Abs):
        arg = _simplify_step(expr.operand)
        if isinstance(arg, Const):
            v = arg.value
            if isinstance(v, complex):
                return _make_const(abs(v))
            return _make_const(abs(v))
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
