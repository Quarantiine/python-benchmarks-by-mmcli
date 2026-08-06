"""Symbolic and numerical integration engine for AST nodes."""

import math
from .ast import (
    AddNode,
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
from .simplifier import simplify


def integrate(node: Node, var: str = "x") -> Node:
    """Compute symbolic antiderivative of AST node with respect to var."""
    res = _integrate_raw(node, var)
    return simplify(res)


def _integrate_raw(node: Node, var: str) -> Node:
    if isinstance(node, Constant):
        return MulNode(Constant(node.value), Variable(var))

    if isinstance(node, Variable):
        if node.name == var:
            return DivNode(PowNode(Variable(var), Constant(2)), Constant(2))
        return MulNode(Variable(node.name), Variable(var))

    if isinstance(node, AddNode):
        return AddNode(_integrate_raw(node.left, var), _integrate_raw(node.right, var))

    if isinstance(node, SubNode):
        return SubNode(_integrate_raw(node.left, var), _integrate_raw(node.right, var))

    if isinstance(node, NegNode):
        return NegNode(_integrate_raw(node.child, var))

    if isinstance(node, MulNode):
        if isinstance(node.left, Constant):
            return MulNode(Constant(node.left.value), _integrate_raw(node.right, var))
        if isinstance(node.right, Constant):
            return MulNode(Constant(node.right.value), _integrate_raw(node.left, var))

    if isinstance(node, PowNode):
        if isinstance(node.left, Variable) and node.left.name == var and isinstance(node.right, Constant):
            n = node.right.value
            if n == -1:
                return LnNode(Variable(var))
            new_n = n + 1
            if new_n == int(new_n):
                new_n = int(new_n)
            return DivNode(PowNode(Variable(var), Constant(new_n)), Constant(new_n))

    if isinstance(node, SinNode):
        if isinstance(node.child, Variable) and node.child.name == var:
            return NegNode(CosNode(Variable(var)))

    if isinstance(node, CosNode):
        if isinstance(node.child, Variable) and node.child.name == var:
            return SinNode(Variable(var))

    if isinstance(node, ExpNode):
        if isinstance(node.child, Variable) and node.child.name == var:
            return ExpNode(Variable(var))

    if isinstance(node, LnNode):
        if isinstance(node.child, Variable) and node.child.name == var:
            return SubNode(MulNode(Variable(var), LnNode(Variable(var))), Variable(var))

    if isinstance(node, SqrtNode):
        if isinstance(node.child, Variable) and node.child.name == var:
            return DivNode(PowNode(Variable(var), Constant(1.5)), Constant(1.5))

    # Fallback to numerical approximation node or error if unhandled
    raise NotImplementedError(f"Symbolic integration not supported for node: {node}")


def definite_integrate(node: Node, var: str = "x", lower: float = 0.0, upper: float = 1.0, n: int = 1000) -> float:
    """Compute definite integral numerically using Simpson's 1/3 rule."""
    if n % 2 == 1:
        n += 1
    lower, upper = float(lower), float(upper)
    h = (upper - lower) / n
    total = node.evaluate({var: lower}) + node.evaluate({var: upper})
    for i in range(1, n):
        x_i = lower + i * h
        weight = 4.0 if i % 2 == 1 else 2.0
        total += weight * node.evaluate({var: x_i})
    return total * (h / 3.0)
