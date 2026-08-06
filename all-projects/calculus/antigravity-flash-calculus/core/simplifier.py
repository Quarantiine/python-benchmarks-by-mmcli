"""Recursive algebraic expression simplifier and constant folder."""

import math
from typing import Optional

from .ast import (
    AcosNode,
    AddNode,
    AsinNode,
    AtanNode,
    Constant,
    CosNode,
    DivNode,
    ExpNode,
    LnNode,
    MulNode,
    NegNode,
    Node,
    PowNode,
    SinNode,
    SqrtNode,
    SubNode,
    TanNode,
    Variable,
)



def simplify(node: Node) -> Node:
    """Recursively simplify AST node until a fixed point is reached."""
    current = node
    for _ in range(15):
        simplified = _simplify_pass(current)
        if str(simplified) == str(current):
            return simplified
        current = simplified
    return current


def _simplify_pass(node: Node) -> Node:
    if isinstance(node, (Constant, Variable)):
        return node

    if isinstance(node, NegNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant):
            return Constant(-child.value)
        if isinstance(child, NegNode):
            return child.child
        return NegNode(child)

    if isinstance(node, AddNode):
        left = _simplify_pass(node.left)
        right = _simplify_pass(node.right)

        # 0 + x -> x, x + 0 -> x
        if isinstance(left, Constant) and left.value == 0:
            return right
        if isinstance(right, Constant) and right.value == 0:
            return left

        # Constant folding: c1 + c2
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value + right.value)

        # Addition with negative: x + (-y) -> x - y, (-x) + y -> y - x
        if isinstance(right, NegNode):
            return _simplify_pass(SubNode(left, right.child))
        if isinstance(left, NegNode):
            return _simplify_pass(SubNode(right, left.child))

        # Like terms: x + x -> 2 * x
        if left == right:
            return _simplify_pass(MulNode(Constant(2), left))

        return AddNode(left, right)

    if isinstance(node, SubNode):
        left = _simplify_pass(node.left)
        right = _simplify_pass(node.right)

        # x - 0 -> x
        if isinstance(right, Constant) and right.value == 0:
            return left
        # 0 - x -> -x
        if isinstance(left, Constant) and left.value == 0:
            return _simplify_pass(NegNode(right))

        # Constant folding: c1 - c2
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value - right.value)

        # x - x -> 0
        if left == right:
            return Constant(0)

        # x - (-y) -> x + y
        if isinstance(right, NegNode):
            return _simplify_pass(AddNode(left, right.child))

        return SubNode(left, right)

    if isinstance(node, MulNode):
        left = _simplify_pass(node.left)
        right = _simplify_pass(node.right)

        # 0 * x -> 0, x * 0 -> 0
        if (isinstance(left, Constant) and left.value == 0) or (
            isinstance(right, Constant) and right.value == 0
        ):
            return Constant(0)

        # 1 * x -> x, x * 1 -> x
        if isinstance(left, Constant) and left.value == 1:
            return right
        if isinstance(right, Constant) and right.value == 1:
            return left

        # -1 * x -> -x, x * -1 -> -x
        if isinstance(left, Constant) and left.value == -1:
            return _simplify_pass(NegNode(right))
        if isinstance(right, Constant) and right.value == -1:
            return _simplify_pass(NegNode(left))

        # Constant folding: c1 * c2
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value * right.value)

        # Associative constant multiplication: c1 * (c2 * x) -> (c1*c2) * x
        if isinstance(left, Constant) and isinstance(right, MulNode):
            if isinstance(right.left, Constant):
                return _simplify_pass(
                    MulNode(Constant(left.value * right.left.value), right.right)
                )

        # Put constants on the left: x * c -> c * x
        if isinstance(right, Constant) and not isinstance(left, Constant):
            return MulNode(right, left)

        # Negations: (-x) * y -> -(x * y), x * (-y) -> -(x * y)
        if isinstance(left, NegNode):
            return _simplify_pass(NegNode(MulNode(left.child, right)))
        if isinstance(right, NegNode):
            return _simplify_pass(NegNode(MulNode(left, right.child)))

        return MulNode(left, right)

    if isinstance(node, DivNode):
        left = _simplify_pass(node.left)
        right = _simplify_pass(node.right)

        # 0 / x -> 0
        if isinstance(left, Constant) and left.value == 0:
            return Constant(0)

        # x / 1 -> x
        if isinstance(right, Constant) and right.value == 1:
            return left

        # x / x -> 1
        if left == right:
            return Constant(1)

        # Constant folding: c1 / c2
        if isinstance(left, Constant) and isinstance(right, Constant):
            if right.value != 0:
                res = left.value / right.value
                if res == int(res):
                    return Constant(int(res))
                return Constant(res)

        return DivNode(left, right)

    if isinstance(node, PowNode):
        left = _simplify_pass(node.left)
        right = _simplify_pass(node.right)

        # x ^ 0 -> 1
        if isinstance(right, Constant) and right.value == 0:
            return Constant(1)

        # x ^ 1 -> x
        if isinstance(right, Constant) and right.value == 1:
            return left

        # 0 ^ x -> 0
        if isinstance(left, Constant) and left.value == 0:
            return Constant(0)

        # 1 ^ x -> 1
        if isinstance(left, Constant) and left.value == 1:
            return Constant(1)

        # Constant folding: c1 ^ c2
        if isinstance(left, Constant) and isinstance(right, Constant):
            try:
                val = math.pow(left.value, right.value)
                return Constant(val)
            except (ValueError, OverflowError):
                pass

        return PowNode(left, right)

    if isinstance(node, SinNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 0:
            return Constant(0)
        return SinNode(child)

    if isinstance(node, CosNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 0:
            return Constant(1)
        return CosNode(child)

    if isinstance(node, TanNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 0:
            return Constant(0)
        return TanNode(child)

    if isinstance(node, ExpNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 0:
            return Constant(1)
        if isinstance(child, LnNode):
            return child.child
        return ExpNode(child)

    if isinstance(node, LnNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 1:
            return Constant(0)
        if isinstance(child, ExpNode):
            return child.child
        return LnNode(child)

    if isinstance(node, SqrtNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value >= 0:
            sq = math.sqrt(child.value)
            if sq == int(sq):
                return Constant(int(sq))
        return SqrtNode(child)

    if isinstance(node, AsinNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 0:
            return Constant(0)
        return AsinNode(child)

    if isinstance(node, AcosNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 1:
            return Constant(0)
        return AcosNode(child)

    if isinstance(node, AtanNode):
        child = _simplify_pass(node.child)
        if isinstance(child, Constant) and child.value == 0:
            return Constant(0)
        return AtanNode(child)

    return node

