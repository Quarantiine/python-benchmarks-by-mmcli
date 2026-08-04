"""
Abstract Syntax Tree (AST) for symbolic mathematical expressions.
Provides base Node class and concrete node types for numbers, variables,
basic arithmetic operations (Add, Subtract, Multiply, Divide, Power, Negate),
and transcendental functions (Sin, Cos, Tan, Log, Exp, Sqrt, Asin, Acos, Atan).
"""

import math
from abc import ABC, abstractmethod
from typing import Dict, Union, Set, Optional


class Node(ABC):
    """Abstract base class for all mathematical AST nodes."""

    @abstractmethod
    def evaluate(self, env: Dict[str, float]) -> float:
        """Evaluate the expression given a variable binding environment."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return a human-readable string representation of the expression."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)})"

    @abstractmethod
    def get_variables(self) -> Set[str]:
        """Return a set of all variable names present in this expression."""
        pass

    @abstractmethod
    def clone(self) -> 'Node':
        """Return a deep copy of the AST node."""
        pass

    def __add__(self, other: Union['Node', float, int]) -> 'Node':
        return Add(self, _to_node(other))

    def __radd__(self, other: Union['Node', float, int]) -> 'Node':
        return Add(_to_node(other), self)

    def __sub__(self, other: Union['Node', float, int]) -> 'Node':
        return Subtract(self, _to_node(other))

    def __rsub__(self, other: Union['Node', float, int]) -> 'Node':
        return Subtract(_to_node(other), self)

    def __mul__(self, other: Union['Node', float, int]) -> 'Node':
        return Multiply(self, _to_node(other))

    def __rmul__(self, other: Union['Node', float, int]) -> 'Node':
        return Multiply(_to_node(other), self)

    def __truediv__(self, other: Union['Node', float, int]) -> 'Node':
        return Divide(self, _to_node(other))

    def __rtruediv__(self, other: Union['Node', float, int]) -> 'Node':
        return Divide(_to_node(other), self)

    def __pow__(self, other: Union['Node', float, int]) -> 'Node':
        return Power(self, _to_node(other))

    def __rpow__(self, other: Union['Node', float, int]) -> 'Node':
        return Power(_to_node(other), self)

    def __neg__(self) -> 'Node':
        return Negate(self)


def _to_node(val: Union[Node, float, int, str]) -> Node:
    """Helper to convert numbers, strings, or nodes into AST Nodes."""
    if isinstance(val, Node):
        return val
    if isinstance(val, (int, float)):
        return Number(val)
    if isinstance(val, str):
        # Try parsing or treating as variable / number
        try:
            if "." in val or "e" in val.lower():
                return Number(float(val))
            else:
                return Number(int(val))
        except ValueError:
            return Variable(val)
    raise TypeError(f"Cannot convert {type(val)} to Node")


class Number(Node):
    """Numeric constant node (e.g. 3, 3.14, -5)."""

    def __init__(self, value: Union[int, float]):
        self.value = float(value) if isinstance(value, int) else value

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.value

    def __str__(self) -> str:
        # Format cleanly (e.g., 3.0 -> 3 or 3.14)
        if isinstance(self.value, float) and self.value.is_integer():
            return str(int(self.value))
        return str(self.value)

    def get_variables(self) -> Set[str]:
        return set()

    def clone(self) -> 'Number':
        return Number(self.value)

    def __eq__(self, other):
        return isinstance(other, Number) and math.isclose(self.value, other.value, rel_tol=1e-9, abs_tol=1e-9)

    def __hash__(self):
        return hash((self.__class__, self.value))


class Variable(Node):
    """Variable node (e.g. x, y, t)."""

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, env: Dict[str, float]) -> float:
        if self.name not in env:
            raise ValueError(f"Variable '{self.name}' is not defined in evaluation environment.")
        return env[self.name]

    def __str__(self) -> str:
        return self.name

    def get_variables(self) -> Set[str]:
        return {self.name}

    def clone(self) -> 'Variable':
        return Variable(self.name)

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self):
        return hash((self.__class__, self.name))


class BinaryOp(Node):
    """Abstract base class for binary operations."""

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and 
                self.left == other.left and 
                self.right == other.right)

    def __hash__(self):
        return hash((self.__class__, self.left, self.right))


class Add(BinaryOp):
    """Addition node (left + right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.left.evaluate(env) + self.right.evaluate(env)

    def __str__(self) -> str:
        return f"({str(self.left)} + {str(self.right)})"

    def clone(self) -> 'Add':
        return Add(self.left.clone(), self.right.clone())


class Subtract(BinaryOp):
    """Subtraction node (left - right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.left.evaluate(env) - self.right.evaluate(env)

    def __str__(self) -> str:
        return f"({str(self.left)} - {str(self.right)})"

    def clone(self) -> 'Subtract':
        return Subtract(self.left.clone(), self.right.clone())


class Multiply(BinaryOp):
    """Multiplication node (left * right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.left.evaluate(env) * self.right.evaluate(env)

    def __str__(self) -> str:
        # Use clean precedence formatting if desired, e.g. left * right
        return f"({str(self.left)} * {str(self.right)})"

    def clone(self) -> 'Multiply':
        return Multiply(self.left.clone(), self.right.clone())


class Divide(BinaryOp):
    """Division node (left / right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        denom = self.right.evaluate(env)
        if math.isclose(denom, 0.0, abs_tol=1e-15):
            raise ZeroDivisionError(f"Division by zero in evaluation of {str(self)}")
        return self.left.evaluate(env) / denom

    def __str__(self) -> str:
        return f"({str(self.left)} / {str(self.right)})"

    def clone(self) -> 'Divide':
        return Divide(self.left.clone(), self.right.clone())


class Power(BinaryOp):
    """Exponentiation node (left ^ right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        base = self.left.evaluate(env)
        exponent = self.right.evaluate(env)
        return base ** exponent

    def __str__(self) -> str:
        return f"({str(self.left)} ^ {str(self.right)})"

    def clone(self) -> 'Power':
        return Power(self.left.clone(), self.right.clone())


class UnaryOp(Node):
    """Abstract base class for unary operations."""

    def __init__(self, operand: Node):
        self.operand = operand

    def get_variables(self) -> Set[str]:
        return self.operand.get_variables()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.operand == other.operand

    def __hash__(self):
        return hash((self.__class__, self.operand))


class Negate(UnaryOp):
    """Unary negation node (-operand)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return -self.operand.evaluate(env)

    def __str__(self) -> str:
        return f"-{str(self.operand)}"

    def clone(self) -> 'Negate':
        return Negate(self.operand.clone())


class Sin(UnaryOp):
    """Sine function node (sin(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.sin(self.operand.evaluate(env))

    def __str__(self) -> str:
        return f"sin({str(self.operand)})"

    def clone(self) -> 'Sin':
        return Sin(self.operand.clone())


class Cos(UnaryOp):
    """Cosine function node (cos(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.cos(self.operand.evaluate(env))

    def __str__(self) -> str:
        return f"cos({str(self.operand)})"

    def clone(self) -> 'Cos':
        return Cos(self.operand.clone())


class Tan(UnaryOp):
    """Tangent function node (tan(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.tan(self.operand.evaluate(env))

    def __str__(self) -> str:
        return f"tan({str(self.operand)})"

    def clone(self) -> 'Tan':
        return Tan(self.operand.clone())


class Log(UnaryOp):
    """Natural logarithm node (log(operand) or ln(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.operand.evaluate(env)
        if val <= 0:
            raise ValueError(f"Logarithm argument must be positive, got {val}")
        return math.log(val)

    def __str__(self) -> str:
        return f"log({str(self.operand)})"

    def clone(self) -> 'Log':
        return Log(self.operand.clone())


class Exp(UnaryOp):
    """Exponential function node (exp(operand) or e^operand)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.exp(self.operand.evaluate(env))

    def __str__(self) -> str:
        return f"exp({str(self.operand)})"

    def clone(self) -> 'Exp':
        return Exp(self.operand.clone())


class Sqrt(UnaryOp):
    """Square root function node (sqrt(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.operand.evaluate(env)
        if val < 0:
            raise ValueError(f"Square root argument cannot be negative, got {val}")
        return math.sqrt(val)

    def __str__(self) -> str:
        return f"sqrt({str(self.operand)})"

    def clone(self) -> 'Sqrt':
        return Sqrt(self.operand.clone())


class Asin(UnaryOp):
    """Arcsine function node (asin(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.operand.evaluate(env)
        return math.asin(val)

    def __str__(self) -> str:
        return f"asin({str(self.operand)})"

    def clone(self) -> 'Asin':
        return Asin(self.operand.clone())


class Acos(UnaryOp):
    """Arccosine function node (acos(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.operand.evaluate(env)
        return math.acos(val)

    def __str__(self) -> str:
        return f"acos({str(self.operand)})"

    def clone(self) -> 'Acos':
        return Acos(self.operand.clone())


class Atan(UnaryOp):
    """Arctangent function node (atan(operand))."""

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.operand.evaluate(env)
        return math.atan(val)

    def __str__(self) -> str:
        return f"atan({str(self.operand)})"

    def clone(self) -> 'Atan':
        return Atan(self.operand.clone())
