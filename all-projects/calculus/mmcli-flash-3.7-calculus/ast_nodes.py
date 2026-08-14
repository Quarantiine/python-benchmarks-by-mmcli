"""
Abstract Syntax Tree (AST) for Symbolic Calculus & Mathematical Expressions
===========================================================================
Defines mathematical AST node hierarchy, arithmetic overloads, evaluation,
tree visualizations (Rich & Unicode/ASCII), and LaTeX/infix formatting.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from fractions import Fraction
import math
from typing import Any, Dict, List, Optional, Set, Tuple, Union

try:
    from rich.tree import Tree as RichTree
    from rich.text import Text as RichText
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    RichTree = None  # type: ignore
    RichText = None  # type: ignore


def to_node(val: Union[Node, int, float, Fraction, str]) -> Node:
    """Convert a numeric value or string variable to an AST Node."""
    if isinstance(val, Node):
        return val
    if isinstance(val, (int, float, Fraction)):
        return Constant(val)
    if isinstance(val, str):
        return Variable(val)
    raise TypeError(f"Cannot convert object of type {type(val).__name__} to AST Node.")


class Node(ABC):
    """Abstract base class for all mathematical AST nodes."""

    # Operator precedence levels (higher number = tighter binding)
    PREC_LOWEST = 0
    PREC_ADD = 10
    PREC_SUB = 10
    PREC_MUL = 20
    PREC_DIV = 20
    PREC_NEG = 30
    PREC_POW = 40
    PREC_FUNC = 50
    PREC_ATOM = 60

    @abstractmethod
    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        """Evaluate the numeric value given variable bindings."""
        pass

    @abstractmethod
    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        """Compute the symbolic derivative with respect to `var`."""
        pass

    def simplify(self) -> Node:
        """Return an algebraically simplified form of this node."""
        try:
            from .simplifier import simplify as simplify_fn
            return simplify_fn(self)
        except Exception:
            try:
                from simplifier import simplify as simplify_fn
                return simplify_fn(self)
            except Exception:
                return self

    @abstractmethod
    def to_infix(self, parent_prec: int = 0) -> str:
        """Format node as mathematical infix string."""
        pass

    @abstractmethod
    def to_latex(self) -> str:
        """Format node as LaTeX expression."""
        pass

    @abstractmethod
    def variables(self) -> Set[str]:
        """Return the set of free variables in the expression."""
        pass

    def is_constant(self) -> bool:
        """Check if expression contains no variables."""
        return len(self.variables()) == 0

    def is_zero(self) -> bool:
        """Check if node represents numeric 0."""
        return False

    def is_one(self) -> bool:
        """Check if node represents numeric 1."""
        return False

    def is_negative_one(self) -> bool:
        """Check if node represents numeric -1."""
        return False

    def to_tree_lines(self, prefix: str = "", is_last: bool = True) -> List[str]:
        """Generate lines for Unicode/ASCII tree representation."""
        node_label = self._tree_label()
        connector = "└── " if is_last else "├── "
        lines = [prefix + connector + node_label]
        
        children = self.get_children()
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            lines.extend(child.to_tree_lines(new_prefix, child_is_last))
        return lines

    def to_tree_string(self) -> str:
        """Return full string representation of the AST hierarchy tree."""
        lines = [self._tree_label()]
        children = self.get_children()
        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            lines.extend(child.to_tree_lines("", child_is_last))
        return "\n".join(lines)

    def to_rich_tree(self, parent: Optional[Any] = None) -> Any:
        """Generate a Rich Tree representation of the AST."""
        if not HAS_RICH:
            return self.to_tree_string()
        
        label = self._rich_tree_label()
        tree = parent.add(label) if parent is not None else RichTree(label)
        for child in self.get_children():
            child.to_rich_tree(tree)
        return tree

    @abstractmethod
    def get_children(self) -> List[Node]:
        """Return child AST nodes."""
        pass

    @abstractmethod
    def _tree_label(self) -> str:
        """Return label string for plain tree visualization."""
        pass

    def _rich_tree_label(self) -> Any:
        """Return Rich Text object for tree visualization."""
        if not HAS_RICH:
            return self._tree_label()
        return RichText(self._tree_label(), style="bold")

    # Operator overloads
    def __add__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Add(self, to_node(other))

    def __radd__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Add(to_node(other), self)

    def __sub__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Subtract(self, to_node(other))

    def __rsub__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Subtract(to_node(other), self)

    def __mul__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Multiply(self, to_node(other))

    def __rmul__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Multiply(to_node(other), self)

    def __truediv__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Divide(self, to_node(other))

    def __rtruediv__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Divide(to_node(other), self)

    def __pow__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Power(self, to_node(other))

    def __rpow__(self, other: Union[Node, int, float, Fraction, str]) -> Node:
        return Power(to_node(other), self)

    def __neg__(self) -> Node:
        return Negate(self)

    def __str__(self) -> str:
        return self.to_infix()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_infix()})"


# ============================================================================
# Leaf Nodes (Constant, NamedConstant, Variable)
# ============================================================================

class Constant(Node):
    """Numeric constant node."""

    def __init__(self, value: Union[int, float, Fraction]) -> None:
        if isinstance(value, float) and value.is_integer():
            self.value: Union[int, Fraction, float] = int(value)
        elif isinstance(value, Fraction) and value.denominator == 1:
            self.value = value.numerator
        else:
            self.value = value

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return float(self.value)

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Constant Rule",
                rule_formula=f"d/d{var}[ c ] = 0",
                input_expr=self.to_infix(),
                target_var=var
            )
            res = Constant(0)
            tracker.end_step(raw_result=res.to_infix(), simplified_result=res.to_infix())
            return res
        return Constant(0)

    def to_infix(self, parent_prec: int = 0) -> str:
        if isinstance(self.value, Fraction):
            res = f"{self.value.numerator}/{self.value.denominator}"
            if parent_prec >= self.PREC_DIV:
                return f"({res})"
            return res
        if isinstance(self.value, (int, float)) and self.value < 0:
            res = str(self.value)
            if parent_prec >= self.PREC_NEG:
                return f"({res})"
            return res
        return str(self.value)

    def to_latex(self) -> str:
        if isinstance(self.value, Fraction):
            return f"\\frac{{{self.value.numerator}}}{{{self.value.denominator}}}"
        return str(self.value)

    def get_children(self) -> List[Node]:
        return []

    def _tree_label(self) -> str:
        return f"Constant({self.value})"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText(f"Constant({self.value})", style="bold magenta")

    def variables(self) -> Set[str]:
        return set()

    def is_zero(self) -> bool:
        return self.value == 0

    def is_one(self) -> bool:
        return self.value == 1

    def is_negative_one(self) -> bool:
        return self.value == -1

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Constant):
            return self.value == other.value
        if isinstance(other, (int, float, Fraction)):
            return self.value == other
        return False

    def __hash__(self) -> int:
        return hash(("Constant", float(self.value) if isinstance(self.value, (int, float, Fraction)) else self.value))


class NamedConstant(Node):
    """Named mathematical constant (e.g. pi, e, tau, phi)."""

    def __init__(self, name: str, value: float, latex_name: Optional[str] = None) -> None:
        self.name = name
        self.value = value
        self.latex_name = latex_name or name

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return self.value

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Constant Rule",
                rule_formula=f"d/d{var}[ {self.name} ] = 0",
                input_expr=self.name,
                target_var=var
            )
            res = Constant(0)
            tracker.end_step(raw_result=res.to_infix(), simplified_result=res.to_infix())
            return res
        return Constant(0)

    def to_infix(self, parent_prec: int = 0) -> str:
        return self.name

    def to_latex(self) -> str:
        return f"\\{self.latex_name}" if not self.latex_name.startswith("\\") else self.latex_name

    def get_children(self) -> List[Node]:
        return []

    def _tree_label(self) -> str:
        return f"NamedConstant({self.name} ≈ {self.value:.5f})"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText(self._tree_label(), style="bold italic magenta")

    def variables(self) -> Set[str]:
        return set()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NamedConstant) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("NamedConstant", self.name))


# Predefined named constants
E = NamedConstant("e", math.e, "e")
PI = NamedConstant("pi", math.pi, "pi")
TAU = NamedConstant("tau", math.tau, "tau")
PHI = NamedConstant("phi", (1 + math.sqrt(5)) / 2, "phi")


class Variable(Node):
    """Symbolic variable node (e.g. x, y, t, theta)."""

    def __init__(self, name: str) -> None:
        self.name = name

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        if env is None or self.name not in env:
            raise KeyError(f"Variable '{self.name}' not found in evaluation environment: {env}")
        return float(env[self.name])

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        is_target = (self.name == var)
        rule_name = "Variable Rule" if is_target else "Independent Variable Rule"
        rule_formula = f"d/d{var}[ {var} ] = 1" if is_target else f"d/d{var}[ {self.name} ] = 0 (independent)"
        res = Constant(1) if is_target else Constant(0)

        if tracker is not None:
            tracker.start_step(
                rule_name=rule_name,
                rule_formula=rule_formula,
                input_expr=self.name,
                target_var=var
            )
            tracker.end_step(raw_result=res.to_infix(), simplified_result=res.to_infix())
        return res

    def to_infix(self, parent_prec: int = 0) -> str:
        return self.name

    def to_latex(self) -> str:
        return self.name

    def get_children(self) -> List[Node]:
        return []

    def _tree_label(self) -> str:
        return f"Variable({self.name})"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText(f"Variable({self.name})", style="bold green")

    def variables(self) -> Set[str]:
        return {self.name}

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("Variable", self.name))


# ============================================================================
# Unary Operations (Negation, Abs, Sign)
# ============================================================================

class UnaryOp(Node):
    """Base class for unary operations and single-argument elementary functions."""

    def __init__(self, child: Union[Node, int, float, Fraction, str]) -> None:
        self.child = to_node(child)

    def variables(self) -> Set[str]:
        return self.child.variables()

    def get_children(self) -> List[Node]:
        return [self.child]


class Negate(UnaryOp):
    """Negation node (-x)."""

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return -self.child.evaluate(env)

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Negation Rule",
                rule_formula=f"d/d{var}[ -u ] = -(u')",
                input_expr=self.to_infix(),
                target_var=var
            )

        d_child = self.child.differentiate(var, tracker)
        raw = Negate(d_child)
        sim = raw.simplify()

        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        child_str = self.child.to_infix(self.PREC_NEG)
        res = f"-{child_str}"
        if parent_prec > self.PREC_NEG:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"-{self.child.to_latex()}"

    def _tree_label(self) -> str:
        return "Negate (-)"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText("Negate (-)", style="bold yellow")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Negate) and self.child == other.child

    def __hash__(self) -> int:
        return hash(("Negate", self.child))


# ============================================================================
# Binary Operations (Add, Subtract, Multiply, Divide, Power)
# ============================================================================

class BinaryOp(Node):
    """Base class for binary operations."""

    def __init__(self, left: Union[Node, int, float, Fraction, str], right: Union[Node, int, float, Fraction, str]) -> None:
        self.left = to_node(left)
        self.right = to_node(right)

    def variables(self) -> Set[str]:
        return self.left.variables() | self.right.variables()

    def get_children(self) -> List[Node]:
        return [self.left, self.right]


class Add(BinaryOp):
    """Addition node (left + right)."""

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return self.left.evaluate(env) + self.right.evaluate(env)

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Sum Rule",
                rule_formula=f"d/d{var}[ u + v ] = u' + v'",
                input_expr=self.to_infix(),
                target_var=var
            )

        du = self.left.differentiate(var, tracker)
        dv = self.right.differentiate(var, tracker)
        raw = Add(du, dv)
        sim = raw.simplify()

        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        # Addition is associative: left needs PREC_ADD, right needs PREC_ADD
        left_str = self.left.to_infix(self.PREC_ADD)
        right_str = self.right.to_infix(self.PREC_ADD)
        res = f"{left_str} + {right_str}"
        if parent_prec > self.PREC_ADD:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{self.left.to_latex()} + {self.right.to_latex()}"

    def _tree_label(self) -> str:
        return "Add (+)"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText("Add (+)", style="bold gold1")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Add) and (
            (self.left == other.left and self.right == other.right) or
            (self.left == other.right and self.right == other.left)
        )

    def __hash__(self) -> int:
        return hash(("Add", frozenset([self.left, self.right])))


class Subtract(BinaryOp):
    """Subtraction node (left - right)."""

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return self.left.evaluate(env) - self.right.evaluate(env)

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Difference Rule",
                rule_formula=f"d/d{var}[ u - v ] = u' - v'",
                input_expr=self.to_infix(),
                target_var=var
            )

        du = self.left.differentiate(var, tracker)
        dv = self.right.differentiate(var, tracker)
        raw = Subtract(du, dv)
        sim = raw.simplify()

        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        left_str = self.left.to_infix(self.PREC_SUB)
        # Right operand of subtraction must parenthesize if it has lower or equal precedence (+, -)
        right_str = self.right.to_infix(self.PREC_SUB + 1)
        res = f"{left_str} - {right_str}"
        if parent_prec > self.PREC_SUB:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{self.left.to_latex()} - {self.right.to_latex()}"

    def _tree_label(self) -> str:
        return "Subtract (-)"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText("Subtract (-)", style="bold gold1")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Subtract) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("Subtract", self.left, self.right))


class Multiply(BinaryOp):
    """Multiplication node (left * right)."""

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return self.left.evaluate(env) * self.right.evaluate(env)

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        # Check constant multiple optimization
        if self.left.is_constant() and not self.right.is_constant():
            if tracker is not None:
                tracker.start_step(
                    rule_name="Constant Multiple Rule",
                    rule_formula=f"d/d{var}[ c * u ] = c * u'",
                    input_expr=self.to_infix(),
                    target_var=var,
                    notes=f"c = {self.left.to_infix()}"
                )
            dv = self.right.differentiate(var, tracker)
            raw = Multiply(self.left, dv)
            sim = raw.simplify()
            if tracker is not None:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        if self.right.is_constant() and not self.left.is_constant():
            if tracker is not None:
                tracker.start_step(
                    rule_name="Constant Multiple Rule",
                    rule_formula=f"d/d{var}[ u * c ] = c * u'",
                    input_expr=self.to_infix(),
                    target_var=var,
                    notes=f"c = {self.right.to_infix()}"
                )
            du = self.left.differentiate(var, tracker)
            raw = Multiply(du, self.right)
            sim = raw.simplify()
            if tracker is not None:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        # General Product Rule
        if tracker is not None:
            tracker.start_step(
                rule_name="Product Rule",
                rule_formula=f"d/d{var}[ u * v ] = u' * v + u * v'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.left.to_infix()}, v = {self.right.to_infix()}"
            )

        du = self.left.differentiate(var, tracker)
        dv = self.right.differentiate(var, tracker)
        raw = Add(Multiply(du, self.right), Multiply(self.left, dv))
        sim = raw.simplify()

        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        left_str = self.left.to_infix(self.PREC_MUL)
        right_str = self.right.to_infix(self.PREC_MUL)
        res = f"{left_str} * {right_str}"
        if parent_prec > self.PREC_MUL:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{self.left.to_latex()} \\cdot {self.right.to_latex()}"

    def _tree_label(self) -> str:
        return "Multiply (*)"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText("Multiply (*)", style="bold dark_orange")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Multiply) and (
            (self.left == other.left and self.right == other.right) or
            (self.left == other.right and self.right == other.left)
        )

    def __hash__(self) -> int:
        return hash(("Multiply", frozenset([self.left, self.right])))


class Divide(BinaryOp):
    """Division node (left / right)."""

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        denom = self.right.evaluate(env)
        if denom == 0:
            return float('nan')
        return self.left.evaluate(env) / denom

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        # Constant denominator optimization: (u / c)' = u' / c
        if self.right.is_constant() and not self.left.is_constant():
            if tracker is not None:
                tracker.start_step(
                    rule_name="Constant Denominator Rule",
                    rule_formula=f"d/d{var}[ u / c ] = u' / c",
                    input_expr=self.to_infix(),
                    target_var=var,
                    notes=f"c = {self.right.to_infix()}"
                )
            du = self.left.differentiate(var, tracker)
            raw = Divide(du, self.right)
            sim = raw.simplify()
            if tracker is not None:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        # Quotient Rule
        if tracker is not None:
            tracker.start_step(
                rule_name="Quotient Rule",
                rule_formula=f"d/d{var}[ u / v ] = (u' * v - u * v') / (v^2)",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.left.to_infix()}, v = {self.right.to_infix()}"
            )

        du = self.left.differentiate(var, tracker)
        dv = self.right.differentiate(var, tracker)

        num = Subtract(Multiply(du, self.right), Multiply(self.left, dv))
        den = Power(self.right, Constant(2))
        raw = Divide(num, den)
        sim = raw.simplify()

        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        left_str = self.left.to_infix(self.PREC_DIV)
        right_str = self.right.to_infix(self.PREC_DIV + 1)
        res = f"{left_str} / {right_str}"
        if parent_prec > self.PREC_DIV:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"\\frac{{{self.left.to_latex()}}}{{{self.right.to_latex()}}}"

    def _tree_label(self) -> str:
        return "Divide (/)"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText("Divide (/)", style="bold dark_orange")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Divide) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("Divide", self.left, self.right))


class Power(BinaryOp):
    """Exponentiation node (base ^ exponent)."""

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        base_val = self.left.evaluate(env)
        exp_val = self.right.evaluate(env)
        try:
            return math.pow(base_val, exp_val)
        except (ValueError, OverflowError):
            return float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        base_has_var = var in self.left.variables()
        exp_has_var = var in self.right.variables()

        # Case 1: Constant w.r.t var
        if not base_has_var and not exp_has_var:
            if tracker is not None:
                tracker.start_step(
                    rule_name="Constant Rule",
                    rule_formula=f"d/d{var}[ c ] = 0",
                    input_expr=self.to_infix(),
                    target_var=var
                )
                res = Constant(0)
                tracker.end_step(raw_result=res.to_infix(), simplified_result=res.to_infix())
                return res
            return Constant(0)

        # Case 2: Standard Power Rule u(x)^n where n is constant
        if base_has_var and not exp_has_var:
            if tracker is not None:
                tracker.start_step(
                    rule_name="Power Rule",
                    rule_formula=f"d/d{var}[ u^n ] = n * u^(n-1) * u'",
                    input_expr=self.to_infix(),
                    target_var=var,
                    notes=f"u = {self.left.to_infix()}, n = {self.right.to_infix()}"
                )

            du = self.left.differentiate(var, tracker)
            # n * u^(n-1) * u'
            raw = Multiply(
                Multiply(self.right, Power(self.left, Subtract(self.right, Constant(1)))),
                du
            )
            sim = raw.simplify()
            if tracker is not None:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        # Case 3: Exponential Rule a^u(x) where a is constant
        if not base_has_var and exp_has_var:
            if tracker is not None:
                tracker.start_step(
                    rule_name="Exponential Power Rule",
                    rule_formula=f"d/d{var}[ a^u ] = a^u * ln(a) * u'",
                    input_expr=self.to_infix(),
                    target_var=var,
                    notes=f"a = {self.left.to_infix()}, u = {self.right.to_infix()}"
                )

            dv = self.right.differentiate(var, tracker)
            raw = Multiply(
                Multiply(self, Ln(self.left)),
                dv
            )
            sim = raw.simplify()
            if tracker is not None:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        # Case 4: General Power Rule u(x)^v(x)
        if tracker is not None:
            tracker.start_step(
                rule_name="General Power Rule",
                rule_formula=f"d/d{var}[ u^v ] = u^v * (v' * ln(u) + v * u' / u)",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.left.to_infix()}, v = {self.right.to_infix()}"
            )

        du = self.left.differentiate(var, tracker)
        dv = self.right.differentiate(var, tracker)

        term1 = Multiply(dv, Ln(self.left))
        term2 = Divide(Multiply(self.right, du), self.left)
        raw = Multiply(self, Add(term1, term2))
        sim = raw.simplify()

        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        # Exponentiation is right-associative: base gets PREC_POW + 1, exp gets PREC_POW
        left_str = self.left.to_infix(self.PREC_POW + 1)
        right_str = self.right.to_infix(self.PREC_POW)
        res = f"{left_str} ^ {right_str}"
        if parent_prec > self.PREC_POW:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{{{self.left.to_latex()}}}^{{{self.right.to_latex()}}}"

    def _tree_label(self) -> str:
        return "Power (^)"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText("Power (^)", style="bold purple")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Power) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("Power", self.left, self.right))


# ============================================================================
# Elementary Functions
# ============================================================================

class FunctionNode(UnaryOp):
    """Base class for elementary mathematical functions with chain rule support."""

    func_name: str = ""
    latex_name: str = ""

    def to_infix(self, parent_prec: int = 0) -> str:
        return f"{self.func_name}({self.child.to_infix(0)})"

    def to_latex(self) -> str:
        name = self.latex_name or self.func_name
        return f"\\{name}\\left({self.child.to_latex()}\\right)"

    def _tree_label(self) -> str:
        return f"{self.__class__.__name__}()"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText(f"{self.__class__.__name__}()", style="bold cyan")

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self.child == other.child

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.child))


class Sin(FunctionNode):
    func_name = "sin"
    latex_name = "sin"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.sin(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [sin]",
                rule_formula=f"d/d{var}[ sin(u) ] = cos(u) * u'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Cos(self.child), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Cos(FunctionNode):
    func_name = "cos"
    latex_name = "cos"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.cos(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [cos]",
                rule_formula=f"d/d{var}[ cos(u) ] = -sin(u) * u'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Negate(Sin(self.child)), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Tan(FunctionNode):
    func_name = "tan"
    latex_name = "tan"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.tan(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [tan]",
                rule_formula=f"d/d{var}[ tan(u) ] = sec(u)^2 * u'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Power(Sec(self.child), Constant(2)), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Sec(FunctionNode):
    func_name = "sec"
    latex_name = "sec"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        c = math.cos(self.child.evaluate(env))
        return 1.0 / c if c != 0 else float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [sec]",
                rule_formula=f"d/d{var}[ sec(u) ] = sec(u) * tan(u) * u'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Multiply(Sec(self.child), Tan(self.child)), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Csc(FunctionNode):
    func_name = "csc"
    latex_name = "csc"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        s = math.sin(self.child.evaluate(env))
        return 1.0 / s if s != 0 else float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [csc]",
                rule_formula=f"d/d{var}[ csc(u) ] = -csc(u) * cot(u) * u'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Negate(Multiply(Csc(self.child), Cot(self.child))), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Cot(FunctionNode):
    func_name = "cot"
    latex_name = "cot"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        t = math.tan(self.child.evaluate(env))
        return 1.0 / t if t != 0 else float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [cot]",
                rule_formula=f"d/d{var}[ cot(u) ] = -csc(u)^2 * u'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Negate(Power(Csc(self.child), Constant(2))), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Asin(FunctionNode):
    func_name = "asin"
    latex_name = "arcsin"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.child.evaluate(env)
        return math.asin(val) if -1.0 <= val <= 1.0 else float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [arcsin]",
                rule_formula=f"d/d{var}[ asin(u) ] = u' / sqrt(1 - u^2)",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        denom = Sqrt(Subtract(Constant(1), Power(self.child, Constant(2))))
        raw = Divide(du, denom)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Acos(FunctionNode):
    func_name = "acos"
    latex_name = "arccos"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.child.evaluate(env)
        return math.acos(val) if -1.0 <= val <= 1.0 else float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [arccos]",
                rule_formula=f"d/d{var}[ acos(u) ] = -u' / sqrt(1 - u^2)",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        denom = Sqrt(Subtract(Constant(1), Power(self.child, Constant(2))))
        raw = Divide(Negate(du), denom)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Atan(FunctionNode):
    func_name = "atan"
    latex_name = "arctan"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.atan(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [arctan]",
                rule_formula=f"d/d{var}[ atan(u) ] = u' / (1 + u^2)",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        denom = Add(Constant(1), Power(self.child, Constant(2)))
        raw = Divide(du, denom)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Sinh(FunctionNode):
    func_name = "sinh"
    latex_name = "sinh"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.sinh(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [sinh]",
                rule_formula=f"d/d{var}[ sinh(u) ] = cosh(u) * u'",
                input_expr=self.to_infix(),
                target_var=var
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Cosh(self.child), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Cosh(FunctionNode):
    func_name = "cosh"
    latex_name = "cosh"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.cosh(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [cosh]",
                rule_formula=f"d/d{var}[ cosh(u) ] = sinh(u) * u'",
                input_expr=self.to_infix(),
                target_var=var
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Sinh(self.child), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Tanh(FunctionNode):
    func_name = "tanh"
    latex_name = "tanh"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return math.tanh(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [tanh]",
                rule_formula=f"d/d{var}[ tanh(u) ] = (1 - tanh(u)^2) * u'",
                input_expr=self.to_infix(),
                target_var=var
            )
        du = self.child.differentiate(var, tracker)
        sech_sq = Subtract(Constant(1), Power(Tanh(self.child), Constant(2)))
        raw = Multiply(sech_sq, du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Exp(FunctionNode):
    func_name = "exp"
    latex_name = "exp"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.child.evaluate(env)
        try:
            return math.exp(val)
        except OverflowError:
            return float('inf')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [exp]",
                rule_formula=f"d/d{var}[ exp(u) ] = exp(u) * u'",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(self, du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Ln(FunctionNode):
    """Natural logarithm node ln(x)."""
    func_name = "ln"
    latex_name = "ln"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.child.evaluate(env)
        return math.log(val) if val > 0 else float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [ln]",
                rule_formula=f"d/d{var}[ ln(u) ] = u' / u",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Divide(du, self.child)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Log(Node):
    """Logarithm with arbitrary base: log_base(x)."""

    def __init__(self, child: Union[Node, int, float, Fraction, str], base: Optional[Union[Node, int, float, Fraction, str]] = None) -> None:
        self.child = to_node(child)
        self.base = to_node(base) if base is not None else Constant(10)

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.child.evaluate(env)
        b = self.base.evaluate(env)
        if val <= 0 or b <= 0 or b == 1.0:
            return float('nan')
        return math.log(val, b)

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [log_b]",
                rule_formula=f"d/d{var}[ log_b(u) ] = u' / (u * ln(b))",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"b = {self.base.to_infix()}, u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        denom = Multiply(self.child, Ln(self.base))
        raw = Divide(du, denom)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        if self.base == Constant(10):
            return f"log({self.child.to_infix(0)})"
        return f"log({self.child.to_infix(0)}, {self.base.to_infix(0)})"

    def to_latex(self) -> str:
        if self.base == Constant(10):
            return f"\\log\\left({self.child.to_latex()}\\right)"
        return f"\\log_{{{self.base.to_latex()}}}\\left({self.child.to_latex()}\\right)"

    def get_children(self) -> List[Node]:
        return [self.child, self.base]

    def _tree_label(self) -> str:
        return f"Log(base={self.base})"

    def _rich_tree_label(self) -> Any:
        if not HAS_RICH:
            return self._tree_label()
        return RichText(self._tree_label(), style="bold cyan")

    def variables(self) -> Set[str]:
        return self.child.variables() | self.base.variables()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Log) and self.child == other.child and self.base == other.base

    def __hash__(self) -> int:
        return hash(("Log", self.child, self.base))


class Sqrt(FunctionNode):
    """Square root node: sqrt(x)."""
    func_name = "sqrt"
    latex_name = "sqrt"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        val = self.child.evaluate(env)
        return math.sqrt(val) if val >= 0 else float('nan')

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [sqrt]",
                rule_formula=f"d/d{var}[ sqrt(u) ] = u' / (2 * sqrt(u))",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        denom = Multiply(Constant(2), Sqrt(self.child))
        raw = Divide(du, denom)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_latex(self) -> str:
        return f"\\sqrt{{{self.child.to_latex()}}}"


class Abs(FunctionNode):
    """Absolute value node: abs(x) or |x|."""
    func_name = "abs"
    latex_name = "abs"

    def evaluate(self, env: Optional[Dict[str, float]] = None) -> float:
        return abs(self.child.evaluate(env))

    def differentiate(self, var: str = "x", tracker: Optional[Any] = None) -> Node:
        if tracker is not None:
            tracker.start_step(
                rule_name="Chain Rule [abs]",
                rule_formula=f"d/d{var}[ |u| ] = (u / |u|) * u'  (u != 0)",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Divide(self.child, Abs(self.child)), du)
        sim = raw.simplify()
        if tracker is not None:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        return f"abs({self.child.to_infix(0)})"

    def to_latex(self) -> str:
        return f"\\left|{self.child.to_latex()}\\right|"


# Function aliases
ArcSin = Asin
ArcCos = Acos
ArcTan = Atan
