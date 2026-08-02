"""
Symbolic Abstract Syntax Tree (AST) definitions for symbolic calculus engine.

Provides core expression classes representing constants, variables, binary operators,
unary operators, and elementary math functions with operator overloading.
"""

from abc import ABC, abstractmethod
import math
from typing import Dict, Set, Union, Any, Optional

Number = Union[int, float]


class Expr(ABC):
    """Abstract base class for all symbolic expressions in the AST."""

    @abstractmethod
    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        """Evaluate expression numerically given a variable binding dictionary env."""
        pass

    @abstractmethod
    def free_symbols(self) -> Set[str]:
        """Return the set of free symbol/variable names present in this expression."""
        pass

    @abstractmethod
    def subs(self, var: str, replacement: "Expr") -> "Expr":
        """Substitute all occurrences of symbol `var` with `replacement` expression."""
        pass

    # Operator Overloading for Native Python Expressions
    def __add__(self, other: Any) -> "Expr":
        return Add(self, _to_expr(other))

    def __radd__(self, other: Any) -> "Expr":
        return Add(_to_expr(other), self)

    def __sub__(self, other: Any) -> "Expr":
        return Sub(self, _to_expr(other))

    def __rsub__(self, other: Any) -> "Expr":
        return Sub(_to_expr(other), self)

    def __mul__(self, other: Any) -> "Expr":
        return Mul(self, _to_expr(other))

    def __rmul__(self, other: Any) -> "Expr":
        return Mul(_to_expr(other), self)

    def __truediv__(self, other: Any) -> "Expr":
        return Div(self, _to_expr(other))

    def __rtruediv__(self, other: Any) -> "Expr":
        return Div(_to_expr(other), self)

    def __pow__(self, other: Any) -> "Expr":
        return Pow(self, _to_expr(other))

    def __rpow__(self, other: Any) -> "Expr":
        return Pow(_to_expr(other), self)

    def __neg__(self) -> "Expr":
        return Neg(self)

    def __pos__(self) -> "Expr":
        return self


def _to_expr(val: Any) -> Expr:
    """Helper to convert numbers to Const and keep Expr intact."""
    if isinstance(val, Expr):
        return val
    if isinstance(val, (int, float)):
        return Const(val)
    raise TypeError(f"Cannot convert object of type {type(val)} to Expr")


class Const(Expr):
    """Represents a constant numeric scalar value (int or float)."""

    def __init__(self, value: Number):
        if isinstance(value, float) and value.is_integer():
            self.value: Number = int(value)
        else:
            self.value = value

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return float(self.value)

    def free_symbols(self) -> Set[str]:
        return set()

    def subs(self, var: str, replacement: Expr) -> Expr:
        return self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Const):
            return math.isclose(self.value, other.value, rel_tol=1e-9, abs_tol=1e-9)
        if isinstance(other, (int, float)):
            return math.isclose(self.value, other, rel_tol=1e-9, abs_tol=1e-9)
        return False

    def __hash__(self) -> int:
        return hash(("Const", float(self.value)))

    def __repr__(self) -> str:
        return f"Const({self.value})"

    def __str__(self) -> str:
        return str(self.value)


class Symbol(Expr):
    """Represents a named variable symbol (e.g., 'x', 'y', 't')."""

    def __init__(self, name: str):
        if not name or not isinstance(name, str):
            raise ValueError("Symbol name must be a non-empty string.")
        self.name = name

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        if env is not None and self.name in env:
            return float(env[self.name])
        raise ValueError(f"Variable '{self.name}' not provided in evaluation environment.")

    def free_symbols(self) -> Set[str]:
        return {self.name}

    def subs(self, var: str, replacement: Expr) -> Expr:
        if self.name == var:
            return replacement
        return self

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("Symbol", self.name))

    def __repr__(self) -> str:
        return f"Symbol('{self.name}')"

    def __str__(self) -> str:
        return self.name


# Built-in Special Symbols/Constants
E_CONST = Symbol("e")
PI_CONST = Symbol("pi")


class BinaryOp(Expr):
    """Base class for binary operations on two sub-expressions."""

    def __init__(self, left: Expr, right: Expr):
        self.left = _to_expr(left)
        self.right = _to_expr(right)

    def free_symbols(self) -> Set[str]:
        return self.left.free_symbols() | self.right.free_symbols()

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.left, self.right))


class Add(BinaryOp):
    """Addition operator: left + right."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return self.left.eval(env) + self.right.eval(env)

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Add(self.left.subs(var, replacement), self.right.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Add) and self.left == other.left and self.right == other.right

    def __repr__(self) -> str:
        return f"Add({self.left!r}, {self.right!r})"

    def __str__(self) -> str:
        return f"({self.left} + {self.right})"


class Sub(BinaryOp):
    """Subtraction operator: left - right."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return self.left.eval(env) - self.right.eval(env)

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Sub(self.left.subs(var, replacement), self.right.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Sub) and self.left == other.left and self.right == other.right

    def __repr__(self) -> str:
        return f"Sub({self.left!r}, {self.right!r})"

    def __str__(self) -> str:
        return f"({self.left} - {self.right})"


class Mul(BinaryOp):
    """Multiplication operator: left * right."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return self.left.eval(env) * self.right.eval(env)

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Mul(self.left.subs(var, replacement), self.right.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Mul) and self.left == other.left and self.right == other.right

    def __repr__(self) -> str:
        return f"Mul({self.left!r}, {self.right!r})"

    def __str__(self) -> str:
        return f"({self.left} * {self.right})"


class Div(BinaryOp):
    """Division operator: left / right."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        denom = self.right.eval(env)
        if math.isclose(denom, 0.0, abs_tol=1e-15):
            raise ZeroDivisionError("Division by zero during evaluation.")
        return self.left.eval(env) / denom

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Div(self.left.subs(var, replacement), self.right.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Div) and self.left == other.left and self.right == other.right

    def __repr__(self) -> str:
        return f"Div({self.left!r}, {self.right!r})"

    def __str__(self) -> str:
        return f"({self.left} / {self.right})"


class Pow(BinaryOp):
    """Exponentiation operator: base ^ exp."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        base_val = self.left.eval(env)
        exp_val = self.right.eval(env)
        return math.pow(base_val, exp_val)

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Pow(self.left.subs(var, replacement), self.right.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Pow) and self.left == other.left and self.right == other.right

    def __repr__(self) -> str:
        return f"Pow({self.left!r}, {self.right!r})"

    def __str__(self) -> str:
        return f"({self.left} ^ {self.right})"


class UnaryOp(Expr):
    """Base class for unary operations on a single operand."""

    def __init__(self, operand: Expr):
        self.operand = _to_expr(operand)

    def free_symbols(self) -> Set[str]:
        return self.operand.free_symbols()

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.operand))


class Neg(UnaryOp):
    """Unary negation operator: -operand."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return -self.operand.eval(env)

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Neg(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Neg) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Neg({self.operand!r})"

    def __str__(self) -> str:
        return f"-({self.operand})"


class Function(UnaryOp):
    """Base class for mathematical functions f(arg)."""
    pass


class Sin(Function):
    """Trigonometric Sine function: sin(x)."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.sin(self.operand.eval(env))

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Sin(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Sin) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Sin({self.operand!r})"

    def __str__(self) -> str:
        return f"sin({self.operand})"


class Cos(Function):
    """Trigonometric Cosine function: cos(x)."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.cos(self.operand.eval(env))

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Cos(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Cos) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Cos({self.operand!r})"

    def __str__(self) -> str:
        return f"cos({self.operand})"


class Tan(Function):
    """Trigonometric Tangent function: tan(x)."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.tan(self.operand.eval(env))

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Tan(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Tan) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Tan({self.operand!r})"

    def __str__(self) -> str:
        return f"tan({self.operand})"


class Exp(Function):
    """Natural exponential function: exp(x) = e^x."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.exp(self.operand.eval(env))

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Exp(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Exp) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Exp({self.operand!r})"

    def __str__(self) -> str:
        return f"exp({self.operand})"


class Ln(Function):
    """Natural logarithm function: ln(x)."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.operand.eval(env)
        if val <= 0:
            raise ValueError("Domain error: ln argument must be positive.")
        return math.log(val)

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Ln(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Ln) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Ln({self.operand!r})"

    def __str__(self) -> str:
        return f"ln({self.operand})"


class Sqrt(Function):
    """Square root function: sqrt(x)."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.operand.eval(env)
        if val < 0:
            raise ValueError("Domain error: sqrt argument must be non-negative.")
        return math.sqrt(val)

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Sqrt(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Sqrt) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Sqrt({self.operand!r})"

    def __str__(self) -> str:
        return f"sqrt({self.operand})"


class Abs(Function):
    """Absolute value function: abs(x)."""

    def eval(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.fabs(self.operand.eval(env))

    def subs(self, var: str, replacement: Expr) -> Expr:
        return Abs(self.operand.subs(var, replacement))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Abs) and self.operand == other.operand

    def __repr__(self) -> str:
        return f"Abs({self.operand!r})"

    def __str__(self) -> str:
        return f"abs({self.operand})"
