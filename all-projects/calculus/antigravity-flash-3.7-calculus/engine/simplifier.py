"""
Algebraic Simplification Engine
===============================
Implements recursive algebraic reduction, constant folding with exact fractions,
identity laws, term collection, and power combining.
"""

from __future__ import annotations
from fractions import Fraction
import math
from typing import Optional, Tuple, Union
from .ast_nodes import (
    Node, Constant, Variable, NamedConstant,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Sec, Csc, Cot,
    Asin, Acos, Atan, Sinh, Cosh, Tanh,
    Exp, Ln, Log, Sqrt, Abs,
    E, PI, _to_node
)


def _is_num(node: Node, val: Union[int, float]) -> bool:
    if isinstance(node, Constant):
        if isinstance(node.value, (int, float)):
            return math.isclose(node.value, val, abs_tol=1e-12)
        if isinstance(node.value, Fraction):
            return node.value == val
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
    return (node, Constant(1))


def simplify_pass(node: Node) -> Node:
    """Single-pass bottom-up simplification."""
    # 1. Leaf nodes
    if isinstance(node, Constant):
        if isinstance(node.value, float) and node.value.is_integer():
            return Constant(int(node.value))
        if isinstance(node.value, Fraction) and node.value.denominator == 1:
            return Constant(node.value.numerator)
        return node

    if isinstance(node, (Variable, NamedConstant)):
        return node

    # 2. Negate
    if isinstance(node, Negate):
        child = simplify_pass(node.child)
        if isinstance(child, Constant):
            return Constant(-child.value)
        if isinstance(child, Negate):
            return child.child
        if isinstance(child, Subtract):
            return Subtract(child.right, child.left)
        return Negate(child)

    # 3. Add
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
            return Constant(left.value + right.value)

        # x + (-y) = x - y
        if isinstance(right, Negate):
            return simplify_pass(Subtract(left, right.child))
        if isinstance(left, Negate):
            return simplify_pass(Subtract(right, left.child))

        # Like terms combining: c1*x + c2*x = (c1 + c2)*x
        c1, base1 = _get_coeff_and_base(left)
        c2, base2 = _get_coeff_and_base(right)
        if base1 == base2 and not isinstance(base1, Constant):
            tot = c1 + c2
            if tot == 0:
                return Constant(0)
            if tot == 1:
                return base1
            if tot == -1:
                return Negate(base1)
            return Multiply(Constant(tot), base1)

        # Associative grouping with constants: (expr + c1) + c2 = expr + (c1 + c2)
        if isinstance(left, Add) and isinstance(left.right, Constant) and isinstance(right, Constant):
            return Add(left.left, Constant(left.right.value + right.value))
        if isinstance(right, Add) and isinstance(right.right, Constant) and isinstance(left, Constant):
            return Add(right.left, Constant(right.right.value + left.value))

        return Add(left, right)

    # 4. Subtract
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
            return Constant(left.value - right.value)

        # x - (-y) = x + y
        if isinstance(right, Negate):
            return simplify_pass(Add(left, right.child))

        # Like terms combining: c1*x - c2*x = (c1 - c2)*x
        c1, base1 = _get_coeff_and_base(left)
        c2, base2 = _get_coeff_and_base(right)
        if base1 == base2 and not isinstance(base1, Constant):
            tot = c1 - c2
            if tot == 0:
                return Constant(0)
            if tot == 1:
                return base1
            if tot == -1:
                return Negate(base1)
            return Multiply(Constant(tot), base1)

        return Subtract(left, right)

    # 5. Multiply
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
            return Constant(left.value * right.value)

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
            return simplify_pass(Multiply(Constant(left.value * right.left.value), right.right))
        if isinstance(right, Constant) and isinstance(left, Multiply) and isinstance(left.left, Constant):
            return simplify_pass(Multiply(Constant(right.value * left.left.value), left.right))

        # Powers combining: x^a * x^b = x^(a + b)
        b1, e1 = _get_base_and_exp(left)
        b2, e2 = _get_base_and_exp(right)
        if b1 == b2:
            return simplify_pass(Power(b1, Add(e1, e2)))

        # Canonical ordering: put Constant first (e.g. x * 3 -> 3 * x)
        if isinstance(right, Constant) and not isinstance(left, Constant):
            return Multiply(right, left)

        return Multiply(left, right)

    # 6. Divide
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
            if right.value == 0:
                return Divide(left, right)
            if isinstance(left.value, int) and isinstance(right.value, int):
                frac = Fraction(left.value, right.value)
                return Constant(frac.numerator if frac.denominator == 1 else frac)
            return Constant(left.value / right.value)

        # (-u) / (-v) = u / v
        if isinstance(left, Negate) and isinstance(right, Negate):
            return simplify_pass(Divide(left.child, right.child))
        if isinstance(left, Negate):
            return simplify_pass(Negate(Divide(left.child, right)))
        if isinstance(right, Negate):
            return simplify_pass(Negate(Divide(left, right.child)))

        # Powers dividing: x^a / x^b = x^(a - b)
        b1, e1 = _get_base_and_exp(left)
        b2, e2 = _get_base_and_exp(right)
        if b1 == b2:
            return simplify_pass(Power(b1, Subtract(e1, e2)))

        # (c1 * x) / (c2 * x) = c1 / c2
        if isinstance(left, Multiply) and isinstance(right, Multiply):
            c1, base1 = _get_coeff_and_base(left)
            c2, base2 = _get_coeff_and_base(right)
            if base1 == base2 and c2 != 0:
                return simplify_pass(Divide(Constant(c1), Constant(c2)))

        # (c * x) / x = c
        if isinstance(left, Multiply):
            c1, base1 = _get_coeff_and_base(left)
            if base1 == right:
                return Constant(c1)

        return Divide(left, right)

    # 7. Power
    if isinstance(node, Power):
        left = simplify_pass(node.left)
        right = simplify_pass(node.right)

        # x ^ 0 = 1
        if _is_num(right, 0):
            return Constant(1)

        # x ^ 1 = x
        if _is_num(right, 1):
            return left

        # 0 ^ x = 0 (for non-zero x)
        if _is_num(left, 0) and not _is_num(right, 0):
            return Constant(0)

        # 1 ^ x = 1
        if _is_num(left, 1):
            return Constant(1)

        # Constant ^ Constant
        if isinstance(left, Constant) and isinstance(right, Constant):
            if isinstance(right.value, int) and -10 <= right.value <= 10:
                if isinstance(left.value, int) and right.value >= 0:
                    return Constant(left.value ** right.value)
                if isinstance(left.value, Fraction):
                    return Constant(left.value ** right.value)
            try:
                res = math.pow(float(left.value), float(right.value))
                if res.is_integer():
                    return Constant(int(res))
                return Constant(res)
            except Exception:
                pass

        # (u ^ a) ^ b = u ^ (a * b)
        if isinstance(left, Power):
            return simplify_pass(Power(left.left, Multiply(left.right, right)))

        # exp(ln(x)) = x
        if isinstance(left, Exp) and isinstance(left.child, Ln):
            return simplify_pass(left.child.child)

        return Power(left, right)

    # 8. Functions
    if isinstance(node, Sin):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        return Sin(child)

    if isinstance(node, Cos):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(1)
        return Cos(child)

    if isinstance(node, Tan):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        return Tan(child)

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
        if child == E:
            return Constant(1)
        if isinstance(child, Exp):
            return child.child
        return Ln(child)

    if isinstance(node, Sqrt):
        child = simplify_pass(node.child)
        if _is_num(child, 0):
            return Constant(0)
        if _is_num(child, 1):
            return Constant(1)
        if isinstance(child, Constant) and isinstance(child.value, (int, float)) and child.value > 0:
            root = math.isqrt(int(child.value)) if isinstance(child.value, int) else None
            if root and root * root == child.value:
                return Constant(root)
        if isinstance(child, Power) and _is_num(child.right, 2):
            return Abs(child.left)
        return Sqrt(child)

    if isinstance(node, Abs):
        child = simplify_pass(node.child)
        if isinstance(child, Constant):
            return Constant(abs(child.value))
        if isinstance(child, Negate):
            return Abs(child.child)
        return Abs(child)

    if isinstance(node, Log):
        child = simplify_pass(node.child)
        base = simplify_pass(node.base)
        if _is_num(child, 1):
            return Constant(0)
        if child == base:
            return Constant(1)
        return Log(child, base)

    return node


def simplify(node: Node, max_passes: int = 8) -> Node:
    """Iteratively simplifies an AST node until convergence."""
    curr = node
    for _ in range(max_passes):
        nxt = simplify_pass(curr)
        if nxt == curr:
            break
        curr = nxt
    return curr
