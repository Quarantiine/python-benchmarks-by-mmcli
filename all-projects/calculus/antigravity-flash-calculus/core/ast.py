"""Abstract Syntax Tree (AST) node definitions for symbolic expression manipulation."""

import math


class Node:
    """Base class for all Abstract Syntax Tree nodes."""

    precedence = 0

    def differentiate(self, var: str) -> "Node":
        """Compute symbolic derivative with respect to variable var."""
        raise NotImplementedError

    def evaluate(self, var_map: dict) -> float:
        """Evaluate the AST node numerically given variable values."""
        raise NotImplementedError

    def to_string(self, parent_precedence: int = 0) -> str:
        """Format node as human-readable mathematical string with parens as needed."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.to_string(0)

    def __repr__(self) -> str:
        return self.to_string(0)


class Constant(Node):
    """Numerical constant node (e.g. 5, 3.14)."""

    precedence = 100

    def __init__(self, value: float):
        # Store as int if float is integer value
        if isinstance(value, (int, float)) and value == int(value):
            self.value = int(value)
        else:
            self.value = float(value)

    def differentiate(self, var: str) -> Node:
        return Constant(0)

    def evaluate(self, var_map: dict) -> float:
        return float(self.value)

    def to_string(self, parent_precedence: int = 0) -> str:
        if isinstance(self.value, float):
            # Trim trailing zeros if clean float
            formatted = f"{self.value:.6f}".rstrip("0").rstrip(".")
            return formatted if formatted else "0"
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, Constant) and self.value == other.value

    def __hash__(self):
        return hash(("Constant", self.value))


class Variable(Node):
    """Symbolic variable node (e.g. 'x', 'y')."""

    precedence = 100

    def __init__(self, name: str):
        self.name = name

    def differentiate(self, var: str) -> Node:
        return Constant(1) if self.name == var else Constant(0)

    def evaluate(self, var_map: dict) -> float:
        if self.name not in var_map:
            raise ValueError(f"Variable '{self.name}' not provided in evaluation context.")
        return float(var_map[self.name])

    def to_string(self, parent_precedence: int = 0) -> str:
        return self.name

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self):
        return hash(("Variable", self.name))


class AddNode(Node):
    """Binary addition node (left + right)."""

    precedence = 10

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        return AddNode(self.left.differentiate(var), self.right.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        return self.left.evaluate(var_map) + self.right.evaluate(var_map)

    def to_string(self, parent_precedence: int = 0) -> str:
        s = f"{self.left.to_string(self.precedence)} + {self.right.to_string(self.precedence)}"
        return f"({s})" if parent_precedence > self.precedence else s

    def __eq__(self, other):
        return isinstance(other, AddNode) and self.left == other.left and self.right == other.right


class SubNode(Node):
    """Binary subtraction node (left - right)."""

    precedence = 10

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        return SubNode(self.left.differentiate(var), self.right.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        return self.left.evaluate(var_map) - self.right.evaluate(var_map)

    def to_string(self, parent_precedence: int = 0) -> str:
        s = f"{self.left.to_string(self.precedence)} - {self.right.to_string(self.precedence + 1)}"
        return f"({s})" if parent_precedence > self.precedence else s

    def __eq__(self, other):
        return isinstance(other, SubNode) and self.left == other.left and self.right == other.right


class MulNode(Node):
    """Binary multiplication node (left * right)."""

    precedence = 20

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        # Product Rule: (f * g)' = f' * g + f * g'
        return AddNode(
            MulNode(self.left.differentiate(var), self.right),
            MulNode(self.left, self.right.differentiate(var)),
        )

    def evaluate(self, var_map: dict) -> float:
        return self.left.evaluate(var_map) * self.right.evaluate(var_map)

    def to_string(self, parent_precedence: int = 0) -> str:
        s = f"{self.left.to_string(self.precedence)} * {self.right.to_string(self.precedence)}"
        return f"({s})" if parent_precedence > self.precedence else s

    def __eq__(self, other):
        return isinstance(other, MulNode) and self.left == other.left and self.right == other.right


class DivNode(Node):
    """Binary division node (left / right)."""

    precedence = 20

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        # Quotient Rule: (f / g)' = (f' * g - f * g') / (g ^ 2)
        numerator = SubNode(
            MulNode(self.left.differentiate(var), self.right),
            MulNode(self.left, self.right.differentiate(var)),
        )
        denominator = PowNode(self.right, Constant(2))
        return DivNode(numerator, denominator)

    def evaluate(self, var_map: dict) -> float:
        denom = self.right.evaluate(var_map)
        if denom == 0:
            return float("nan")
        return self.left.evaluate(var_map) / denom

    def to_string(self, parent_precedence: int = 0) -> str:
        s = f"{self.left.to_string(self.precedence)} / {self.right.to_string(self.precedence + 1)}"
        return f"({s})" if parent_precedence > self.precedence else s

    def __eq__(self, other):
        return isinstance(other, DivNode) and self.left == other.left and self.right == other.right


class PowNode(Node):
    """Binary exponentiation node (left ^ right)."""

    precedence = 30

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        # General Power Rule: d/dx(f^g) = f^g * (g' * ln(f) + g * f' / f)
        # Special case: constant exponent g = c: c * f^(c-1) * f'
        if isinstance(self.right, Constant):
            c = self.right.value
            return MulNode(
                MulNode(Constant(c), PowNode(self.left, Constant(c - 1))),
                self.left.differentiate(var),
            )
        # General case using chain rule on exp(g * ln(f))
        term1 = MulNode(self.right.differentiate(var), LnNode(self.left))
        term2 = MulNode(self.right, DivNode(self.left.differentiate(var), self.left))
        return MulNode(PowNode(self.left, self.right), AddNode(term1, term2))

    def evaluate(self, var_map: dict) -> float:
        base = self.left.evaluate(var_map)
        exp = self.right.evaluate(var_map)
        try:
            return math.pow(base, exp)
        except (ValueError, OverflowError):
            return float("nan")

    def to_string(self, parent_precedence: int = 0) -> str:
        s = f"{self.left.to_string(self.precedence + 1)} ^ {self.right.to_string(self.precedence)}"
        return f"({s})" if parent_precedence > self.precedence else s

    def __eq__(self, other):
        return isinstance(other, PowNode) and self.left == other.left and self.right == other.right


class NegNode(Node):
    """Unary negation node (-child)."""

    precedence = 25

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        return NegNode(self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        return -self.child.evaluate(var_map)

    def to_string(self, parent_precedence: int = 0) -> str:
        s = f"-{self.child.to_string(self.precedence)}"
        return f"({s})" if parent_precedence > self.precedence else s

    def __eq__(self, other):
        return isinstance(other, NegNode) and self.child == other.child


class SinNode(Node):
    """Sine function node sin(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx sin(u) = cos(u) * u'
        return MulNode(CosNode(self.child), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        return math.sin(self.child.evaluate(var_map))

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"sin({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, SinNode) and self.child == other.child


class CosNode(Node):
    """Cosine function node cos(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx cos(u) = -sin(u) * u'
        return MulNode(NegNode(SinNode(self.child)), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        return math.cos(self.child.evaluate(var_map))

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"cos({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, CosNode) and self.child == other.child


class TanNode(Node):
    """Tangent function node tan(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx tan(u) = (1 / cos(u)^2) * u'
        sec_sq = DivNode(Constant(1), PowNode(CosNode(self.child), Constant(2)))
        return MulNode(sec_sq, self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        return math.tan(self.child.evaluate(var_map))

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"tan({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, TanNode) and self.child == other.child


class ExpNode(Node):
    """Exponential function node exp(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx exp(u) = exp(u) * u'
        return MulNode(ExpNode(self.child), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        try:
            return math.exp(self.child.evaluate(var_map))
        except OverflowError:
            return float("inf")

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"exp({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, ExpNode) and self.child == other.child


class LnNode(Node):
    """Natural logarithm node ln(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx ln(u) = (1 / u) * u'
        return MulNode(DivNode(Constant(1), self.child), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        val = self.child.evaluate(var_map)
        if val <= 0:
            return float("nan")
        return math.log(val)

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"ln({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, LnNode) and self.child == other.child


class SqrtNode(Node):
    """Square root function node sqrt(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx sqrt(u) = (1 / (2 * sqrt(u))) * u'
        denom = MulNode(Constant(2), SqrtNode(self.child))
        return MulNode(DivNode(Constant(1), denom), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        val = self.child.evaluate(var_map)
        if val < 0:
            return float("nan")
        return math.sqrt(val)

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"sqrt({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, SqrtNode) and self.child == other.child


class AsinNode(Node):
    """Arcsine function node asin(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx asin(u) = (1 / sqrt(1 - u^2)) * u'
        denom = SqrtNode(SubNode(Constant(1), PowNode(self.child, Constant(2))))
        return MulNode(DivNode(Constant(1), denom), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        val = self.child.evaluate(var_map)
        if val < -1 or val > 1:
            return float("nan")
        return math.asin(val)

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"asin({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, AsinNode) and self.child == other.child


class AcosNode(Node):
    """Arccosine function node acos(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx acos(u) = (-1 / sqrt(1 - u^2)) * u'
        denom = SqrtNode(SubNode(Constant(1), PowNode(self.child, Constant(2))))
        return MulNode(DivNode(Constant(-1), denom), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        val = self.child.evaluate(var_map)
        if val < -1 or val > 1:
            return float("nan")
        return math.acos(val)

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"acos({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, AcosNode) and self.child == other.child


class AtanNode(Node):
    """Arctangent function node atan(child)."""

    precedence = 50

    def __init__(self, child: Node):
        self.child = child

    def differentiate(self, var: str) -> Node:
        # d/dx atan(u) = (1 / (1 + u^2)) * u'
        denom = AddNode(Constant(1), PowNode(self.child, Constant(2)))
        return MulNode(DivNode(Constant(1), denom), self.child.differentiate(var))

    def evaluate(self, var_map: dict) -> float:
        return math.atan(self.child.evaluate(var_map))

    def to_string(self, parent_precedence: int = 0) -> str:
        return f"atan({self.child.to_string(0)})"

    def __eq__(self, other):
        return isinstance(other, AtanNode) and self.child == other.child

