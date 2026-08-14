"""
Algebraic Simplification Engine
===============================
Implements multi-pass recursive algebraic simplification, constant folding with exact
fractions, algebraic identities, like-term collection, power combining, and elementary
function evaluations.
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


def _is_num(node: Node, val: Union[int, float, Fraction]) -> bool:
    """Check if node is a numeric constant equal to `val`."""
    if isinstance(node, Constant):
        if isinstance(node.value, (int, float)):
            if isinstance(val, Fraction):
                return math.isclose(float(node.value), float(val), abs_tol=1e-12)
            return math.isclose(float(node.value), float(val), abs_tol=1e-12)
        if isinstance(node.value, Fraction):
            if isinstance(val, Fraction):
                return node.value == val
            return math.isclose(float(node.value), float(val), abs_tol=1e-12)
    return False


def _get_coeff_and_base(node: Node) -> Tuple[Union[int, float, Fraction], Node]:
    """Extract coefficient and core symbolic term for combining like terms."""
    if isinstance(node, Constant):
        return (node.value, Constant(1))
    if isinstance(node, Negate):
        coeff, base = _get_coeff_and_base(node.child)
        return (-coeff, base)
    if isinstance(node, Multiply):
        if isinstance(node.left, Constant):
            coeff, base = _get_coeff_and_base(node.right)
            return (node.left.value * coeff, base)
        if isinstance(node.right, Constant):
            coeff, base = _get_coeff_and_base(node.left)
            return (node.right.value * coeff, base)
    return (1, node)


def _get_base_and_exp(node: Node) -> Tuple[Node, Node]:
    """Extract base and exponent for combining powers."""
    if isinstance(node, Power):
        return (node.left, node.right)
    if isinstance(node, Sqrt):
        return (node.child, Constant(Fraction(1, 2)))
    return (node, Constant(1))


def _make_constant(val: Union[int, float, Fraction]) -> Constant:
    """Create a normalized Constant node."""
    if isinstance(val, float) and val.is_integer():
        return Constant(int(val))
    if isinstance(val, Fraction) and val.denominator == 1:
        return Constant(val.numerator)
    return Constant(val)


def _add_constants(c1: Union[int, float, Fraction], c2: Union[int, float, Fraction]) -> Union[int, float, Fraction]:
    """Exact addition of numbers."""
    if isinstance(c1, Fraction) or isinstance(c2, Fraction):
        return Fraction(c1) + Fraction(c2)
    return c1 + c2


def _sub_constants(c1: Union[int, float, Fraction], c2: Union[int, float, Fraction]) -> Union[int, float, Fraction]:
    """Exact subtraction of numbers."""
    if isinstance(c1, Fraction) or isinstance(c2, Fraction):
        return Fraction(c1) - Fraction(c2)
    return c1 - c2


def _mul_constants(c1: Union[int, float, Fraction], c2: Union[int, float, Fraction]) -> Union[int, float, Fraction]:
    """Exact multiplication of numbers."""
    if isinstance(c1, Fraction) or isinstance(c2, Fraction):
        return Fraction(c1) * Fraction(c2)
    return c1 * c2


def _div_constants(c1: Union[int, float, Fraction], c2: Union[int, float, Fraction]) -> Optional[Union[int, float, Fraction]]:
    """Exact division of numbers."""
    if c2 == 0:
        return None
    if isinstance(c1, int) and isinstance(c2, int):
        frac = Fraction(c1, c2)
        return frac.numerator if frac.denominator == 1 else frac
    if isinstance(c1, Fraction) or isinstance(c2, Fraction):
        frac = Fraction(c1) / Fraction(c2)
        return frac.numerator if frac.denominator == 1 else frac
    return c1 / c2


def simplify_pass(node: Node) -> Node:
    """Single bottom-up algebraic simplification pass."""
    # 1. Leaf nodes
    if isinstance(node, Constant):
        return _make_constant(node.value)

    if isinstance(node, (Variable, NamedConstant)):
        return node

    # 2. Negation
    if isinstance(node, Negate):
        child = simplify_pass(node.child)
        if isinstance(child, Constant):
            return _make_constant(-child.value)
        if isinstance(child, Negate):
            return child.child
        if isinstance(child, Subtract):
            return Subtract(child.right, child.left)
        if _is_num(child, 0):
            return Constant(0)
        return Negate(child)

    # 3. Addition
    if isinstance(node, Add):
        left = simplify_pass(node.left)
        right = simplify_pass(node.right)

        # 0 + x = x, x + 0 = x
        if _is_num(left, 0):
            return right
        if _is_num(right, 0):
            return left

        # Constant + Constant
        if isinstance(left, Constant) and isinstance(right, Constant):
            return _make_constant(_add_constants(left.value, right.value))

        # x + (-y) = x - y
        if isinstance(right, Negate):
            return simplify_pass(Subtract(left, right.child))
        # (-x) + y = y - x
        if isinstance(left, Negate):
            return simplify_pass(Subtract(right, left.child))

        # Like terms combining: c1*x + c2*x = (c1 + c2)*x
        c1, base1 = _get_coeff_and_base(left)
        c2, base2 = _get_coeff_and_base(right)
        if base1 == base2 and not isinstance(base1, Constant):
            tot = _add_constants(c1, c2)
            if tot == 0:
                return Constant(0)
            if tot == 1:
                return base1
            if tot == -1:
                return Negate(base1)
            return Multiply(_make_constant(tot), base1)

        # Associative grouping with constants: (expr + c1) + c2 = expr + (c1 + c2)
        if isinstance(left, Add) and isinstance(left.right, Constant) and isinstance(right, Constant):
            return simplify_pass(Add(left.left, _make_constant(_add_constants(left.right.value, right.value))))
        if isinstance(right, Add) and isinstance(right.right, Constant) and isinstance(left, Constant):
            return simplify_pass(Add(right.left, _make_constant(_add_constants(right.right.value, left.value))))

        # (expr - c1) + c2 = expr + (c2 - c1)
        if isinstance(left, Subtract) and isinstance(left.right, Constant) and isinstance(right, Constant):
            diff_c = _sub_constants(right.value, left.right.value)
            if diff_c >= 0:
                return simplify_pass(Add(left.left, _make_constant(diff_c)))
            else:
                return simplify_pass(Subtract(left.left, _make_constant(-diff_c)))

        # Canonical ordering: put constants on right in addition if one is constant
        if isinstance(left, Constant) and not isinstance(right, Constant):
            return Add(right, left)

        return Add(left, right)

    # 4. Subtraction
    if isinstance(node, Subtract):
        left = simplify_pass(node.left)
        right = simplify_pass(node.right)

        # x - 0 = x
        if _is_num(right, 0):
            return left
        # 0 - x = -x
        if _is_num(left, 0):
            return simplify_pass(Negate(right))

        # x - x = 0
        if left == right:
            return Constant(0)

        # Constant - Constant
        if isinstance(left, Constant) and isinstance(right, Constant):
            return _make_constant(_sub_constants(left.value, right.value))

        # x - (-y) = x + y
        if isinstance(right, Negate):
            return simplify_pass(Add(left, right.child))

        # Like terms combining: c1*x - c2*x = (c1 - c2)*x
        c1, base1 = _get_coeff_and_base(left)
        c2, base2 = _get_coeff_and_base(right)
        if base1 == base2 and not isinstance(base1, Constant):
            tot = _sub_constants(c1, c2)
            if tot == 0:
                return Constant(0)
            if tot == 1:
                return base1
            if tot == -1:
                return Negate(base1)
            return Multiply(_make_constant(tot), base1)

        # (expr + c1) - c2 = expr + (c1 - c2)
        if isinstance(left, Add) and isinstance(left.right, Constant) and isinstance(right, Constant):
            diff_c = _sub_constants(left.right.value, right.value)
            if diff_c >= 0:
                return simplify_pass(Add(left.left, _make_constant(diff_c)))
            else:
                return simplify_pass(Subtract(left.left, _make_constant(-diff_c)))

        # (expr - c1) - c2 = expr - (c1 + c2)
        if isinstance(left, Subtract) and isinstance(left.right, Constant) and isinstance(right, Constant):
            return simplify_pass(Subtract(left.left, _make_constant(_add_constants(left.right.value, right.value))))

        return Subtract(left, right)

    # 5. Multiplication
    if isinstance(node, Multiply):
        left = simplify_pass(node.left)
        right = simplify_pass(node.right)

        # 0 * x = 0, x * 0 = 0
        if _is_num(left, 0) or _is_num(right, 0):
            return Constant(0)

        # 1 * x = x, x * 1 = x
        if _is_num(left, 1):
            return right
        if _is_num(right, 1):
            return left

        # -1 * x = -x, x * -1 = -x
        if _is_num(left, -1):
            return simplify_pass(Negate(right))
        if _is_num(right, -1):
            return simplify_pass(Negate(left))

        # Constant * Constant
        if isinstance(left, Constant) and isinstance(right, Constant):
            return _make_constant(_mul_constants(left.value, right.value))

        # (-u) * (-v) = u * v
        if isinstance(left, Negate) and isinstance(right, Negate):
            return simplify_pass(Multiply(left.child, right.child))
        # (-u) * v = -(u * v)
        if isinstance(left, Negate):
            return simplify_pass(Negate(Multiply(left.child, right)))
        if isinstance(right, Negate):
            return simplify_pass(Negate(Multiply(left, right.child)))

        # Associative grouping: c1 * (c2 * x) = (c1 * c2) * x
        if isinstance(left, Constant) and isinstance(right, Multiply) and isinstance(right.left, Constant):
            return simplify_pass(Multiply(_make_constant(_mul_constants(left.value, right.left.value)), right.right))
        if isinstance(right, Constant) and isinstance(left, Multiply) and isinstance(left.left, Constant):
            return simplify_pass(Multiply(_make_constant(_mul_constants(right.value, left.left.value)), left.right))

        # c1 * (u / c2) = (c1 / c2) * u
        if isinstance(left, Constant) and isinstance(right, Divide) and isinstance(right.right, Constant):
            frac_coeff = _div_constants(left.value, right.right.value)
            if frac_coeff is not None:
                if frac_coeff == 1:
                    return right.left
                if frac_coeff == -1:
                    return simplify_pass(Negate(right.left))
                return simplify_pass(Multiply(_make_constant(frac_coeff), right.left))
        if isinstance(right, Constant) and isinstance(left, Divide) and isinstance(left.right, Constant):
            frac_coeff = _div_constants(right.value, left.right.value)
            if frac_coeff is not None:
                if frac_coeff == 1:
                    return left.left
                if frac_coeff == -1:
                    return simplify_pass(Negate(left.left))
                return simplify_pass(Multiply(_make_constant(frac_coeff), left.left))

        # Powers combining: x^a * x^b = x^(a + b)
        b1, e1 = _get_base_and_exp(left)
        b2, e2 = _get_base_and_exp(right)
        if b1 == b2:
            return simplify_pass(Power(b1, simplify_pass(Add(e1, e2))))

        # Canonical ordering: put Constant first (e.g. x * 3 -> 3 * x)
        if isinstance(right, Constant) and not isinstance(left, Constant):
            return Multiply(right, left)

        return Multiply(left, right)

    # 6. Division
    if isinstance(node, Divide):
        left = simplify_pass(node.left)
        right = simplify_pass(node.right)

        # 0 / x = 0
        if _is_num(left, 0):
            return Constant(0)

        # x / 1 = x
        if _is_num(right, 1):
            return left

        # x / -1 = -x
        if _is_num(right, -1):
            return simplify_pass(Negate(left))

        # x / x = 1
        if left == right:
            return Constant(1)

        # Constant / Constant
        if isinstance(left, Constant) and isinstance(right, Constant):
            res = _div_constants(left.value, right.value)
            if res is not None:
                return _make_constant(res)
            return Divide(left, right)

        # (-u) / (-v) = u / v
        if isinstance(left, Negate) and isinstance(right, Negate):
            return simplify_pass(Divide(left.child, right.child))
        if isinstance(left, Negate):
            return simplify_pass(Negate(Divide(left.child, right)))
        if isinstance(right, Negate):
            return simplify_pass(Negate(Divide(left, right.child)))

        # Constant in numerator / constant: (c1 * u) / c2 = (c1 / c2) * u
        if isinstance(left, Multiply) and isinstance(left.left, Constant) and isinstance(right, Constant):
            frac_coeff = _div_constants(left.left.value, right.value)
            if frac_coeff is not None:
                if frac_coeff == 1:
                    return left.right
                if frac_coeff == -1:
                    return simplify_pass(Negate(left.right))
                return simplify_pass(Multiply(_make_constant(frac_coeff), left.right))

        # Powers dividing: x^a / x^b = x^(a - b)
        b1, e1 = _get_base_and_exp(left)
        b2, e2 = _get_base_and_exp(right)
        if b1 == b2:
            return simplify_pass(Power(b1, simplify_pass(Subtract(e1, e2))))

        return Divide(left, right)

    # 7. Power
    if isinstance(node, Power):
        base = simplify_pass(node.left)
        exp = simplify_pass(node.right)

        # x^0 = 1
        if _is_num(exp, 0):
            return Constant(1)

        # x^1 = x
        if _is_num(exp, 1):
            return base

        # 0^x = 0
        if _is_num(base, 0):
            return Constant(0)

        # 1^x = 1
        if _is_num(base, 1):
            return Constant(1)

        # Constant ^ Constant
        if isinstance(base, Constant) and isinstance(exp, Constant):
            if isinstance(exp.value, int):
                if exp.value >= 0:
                    val = base.value ** exp.value
                    if isinstance(val, (int, float, Fraction)):
                        return _make_constant(val)
                elif exp.value < 0 and base.value != 0:
                    val = Fraction(1, base.value ** (-exp.value)) if isinstance(base.value, int) else (1.0 / (base.value ** (-exp.value)))
                    return _make_constant(val)

        # (x^a)^b = x^(a * b)
        if isinstance(base, Power):
            return simplify_pass(Power(base.left, simplify_pass(Multiply(base.right, exp))))

        # exp(x)^y = exp(x * y)
        if isinstance(base, Exp):
            return simplify_pass(Exp(simplify_pass(Multiply(base.child, exp))))

        return Power(base, exp)

    # 8. Sqrt
    if isinstance(node, Sqrt):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        if _is_num(child, 1):
            return Constant(1)
        if isinstance(child, Constant):
            if isinstance(child.value, (int, float)) and child.value >= 0:
                root = math.isqrt(int(child.value)) if isinstance(child.value, int) else math.sqrt(child.value)
                if root * root == child.value:
                    return _make_constant(int(root))
        if isinstance(child, Power) and _is_num(child.right, 2):
            return child.left
        return Sqrt(child)

    # 9. Elementary Functions
    if isinstance(node, Sin):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        if isinstance(child, Negate):
            return simplify_pass(Negate(Sin(child.child)))
        return Sin(child)

    if isinstance(node, Cos):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(1)
        if isinstance(child, Negate):
            return Cos(child.child)
        return Cos(child)

    if isinstance(node, Tan):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        if isinstance(child, Negate):
            return simplify_pass(Negate(Tan(child.child)))
        return Tan(child)

    if isinstance(node, Sec):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(1)
        return Sec(child)

    if isinstance(node, Csc):
        child = simplify_pass(node.child)
        return Csc(child)

    if isinstance(node, Cot):
        child = simplify_pass(node.child)
        return Cot(child)

    if isinstance(node, Asin):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        return Asin(child)

    if isinstance(node, Acos):
        child = simplify_pass(node.child)
        if _is_num(child, 1):
            return Constant(0)
        return Acos(child)

    if isinstance(node, Atan):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        return Atan(child)

    if isinstance(node, Sinh):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        return Sinh(child)

    if isinstance(node, Cosh):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(1)
        return Cosh(child)

    if isinstance(node, Tanh):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        return Tanh(child)

    if isinstance(node, Exp):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(1)
        if _is_num(child, 1):
            return E
        if isinstance(child, Ln):
            return child.child
        return Exp(child)

    if isinstance(node, Ln):
        child = simplify_pass(node.child)
        if _is_num(child, 1):
            return Constant(0)
        if isinstance(child, NamedConstant) and child.name == "e":
            return Constant(1)
        if isinstance(child, Exp):
            return child.child
        return Ln(child)

    if isinstance(node, Log):
        child = simplify_pass(node.child)
        base = simplify_pass(node.base) if node.base is not None else None
        if _is_num(child, 1):
            return Constant(0)
        if base is not None and child == base:
            return Constant(1)
        return Log(child, base)

    if isinstance(node, Abs):
        child = simplify_pass(node.child)
        if isinstance(child, Constant):
            return _make_constant(abs(child.value))
        return Abs(child)

    return node


def simplify(node: Union[Node, str], max_passes: int = 10) -> Node:
    """
    Perform multi-pass fixed-point algebraic simplification on the AST.
    Iterates until the expression AST stops changing or max_passes is reached.
    """
    if isinstance(node, str):
        from parser import parse_expr
        node = parse_expr(node)

    curr = node
    for _ in range(max_passes):
        simplified = simplify_pass(curr)
        if simplified == curr or simplified.to_infix() == curr.to_infix():
            return simplified
        curr = simplified
    return curr


deep_simplify = simplify
