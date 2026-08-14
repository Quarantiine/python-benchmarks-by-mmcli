"""
Abstract Syntax Tree (AST) for Symbolic Expressions
===================================================
Defines the mathematical AST node hierarchy, arithmetic overloads,
evaluation, tree visualizations, and LaTeX/infix formatting.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from fractions import Fraction
import math
from typing import Any, Dict, Optional, Set, Union
from rich.tree import Tree
from rich.text import Text


def _to_node(val: Union[Node, int, float, Fraction, str]) -> Node:
    if isinstance(val, Node):
        return val
    if isinstance(val, (int, float, Fraction)):
        return Constant(val)
    if isinstance(val, str):
        return Variable(val)
    raise TypeError(f"Cannot convert type {type(val)} to AST Node.")


class Node(ABC):
    """Abstract base class for all mathematical AST nodes."""

    # Operator precedence for infix rendering
    # Higher number = tighter binding
    PREC_ADD = 10
    PREC_SUB = 10
    PREC_MUL = 20
    PREC_DIV = 20
    PREC_NEG = 30
    PREC_POW = 40
    PREC_FUNC = 50
    PREC_ATOM = 60

    @abstractmethod
    def evaluate(self, env: Dict[str, float]) -> float:
        """Evaluate numerical value given variable bindings."""
        pass

    @abstractmethod
    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        """Compute the symbolic derivative with respect to `var`."""
        pass

    @abstractmethod
    def simplify(self) -> Node:
        """Return an algebraically simplified form of this node."""
        pass

    @abstractmethod
    def to_infix(self, parent_prec: int = 0) -> str:
        """Format node as mathematical infix string."""
        pass

    @abstractmethod
    def to_latex(self) -> str:
        """Format node as LaTeX expression."""
        pass

    @abstractmethod
    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        """Generate a Rich Tree representation of the AST."""
        pass

    @abstractmethod
    def variables(self) -> Set[str]:
        """Return the set of free variables in the expression."""
        pass

    def is_constant(self) -> bool:
        """Check if expression contains no variables."""
        return len(self.variables()) == 0

    def is_zero(self) -> bool:
        return False

    def is_one(self) -> bool:
        return False

    def is_negative_one(self) -> bool:
        return False

    # Arithmetic operator overloads
    def __add__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Add(self, _to_node(other))

    def __radd__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Add(_to_node(other), self)

    def __sub__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Subtract(self, _to_node(other))

    def __rsub__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Subtract(_to_node(other), self)

    def __mul__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Multiply(self, _to_node(other))

    def __rmul__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Multiply(_to_node(other), self)

    def __truediv__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Divide(self, _to_node(other))

    def __rtruediv__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Divide(_to_node(other), self)

    def __pow__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Power(self, _to_node(other))

    def __rpow__(self, other: Union[Node, int, float, Fraction]) -> Node:
        return Power(_to_node(other), self)

    def __neg__(self) -> Node:
        return Negate(self)

    def __str__(self) -> str:
        return self.to_infix()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"


# ============================================================================
# Leaf Nodes
# ============================================================================

class Constant(Node):
    """Numerical constant node."""

    def __init__(self, value: Union[int, float, Fraction]) -> None:
        if isinstance(value, float) and value.is_integer():
            self.value: Union[int, Fraction, float] = int(value)
        elif isinstance(value, Fraction) and value.denominator == 1:
            self.value = value.numerator
        else:
            self.value = value

    def evaluate(self, env: Dict[str, float]) -> float:
        return float(self.value)

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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

    def simplify(self) -> Node:
        return self

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

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text(f"Constant({self.value})", style="bold magenta")
        if parent is not None:
            return parent.add(text)
        return Tree(text)

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
        return hash(("Constant", self.value))


class NamedConstant(Node):
    """Named mathematical constant (e.g. pi, e)."""

    def __init__(self, name: str, value: float, latex_name: Optional[str] = None) -> None:
        self.name = name
        self.value = value
        self.latex_name = latex_name or name

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.value

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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

    def simplify(self) -> Node:
        return self

    def to_infix(self, parent_prec: int = 0) -> str:
        return self.name

    def to_latex(self) -> str:
        return f"\\{self.latex_name}" if not self.latex_name.startswith("\\") else self.latex_name

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text(f"NamedConstant({self.name} ≈ {self.value:.5f})", style="bold italic magenta")
        if parent is not None:
            return parent.add(text)
        return Tree(text)

    def variables(self) -> Set[str]:
        return set()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NamedConstant) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("NamedConstant", self.name))


# Common named constants
E = NamedConstant("e", math.e, "e")
PI = NamedConstant("pi", math.pi, "pi")


class Variable(Node):
    """Symbolic variable node (e.g. x, y, t)."""

    def __init__(self, name: str) -> None:
        self.name = name

    def evaluate(self, env: Dict[str, float]) -> float:
        if self.name not in env:
            raise KeyError(f"Variable '{self.name}' not provided in evaluation environment: {env}")
        return env[self.name]

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        is_same = (self.name == var)
        rule_name = "Variable Rule" if is_same else "Independent Variable Rule"
        rule_formula = f"d/d{var}[ {var} ] = 1" if is_same else f"d/d{var}[ {self.name} ] = 0 (independent)"
        res = Constant(1) if is_same else Constant(0)
        
        if tracker:
            tracker.start_step(
                rule_name=rule_name,
                rule_formula=rule_formula,
                input_expr=self.name,
                target_var=var
            )
            tracker.end_step(raw_result=res.to_infix(), simplified_result=res.to_infix())
        return res

    def simplify(self) -> Node:
        return self

    def to_infix(self, parent_prec: int = 0) -> str:
        return self.name

    def to_latex(self) -> str:
        return self.name

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text(f"Variable({self.name})", style="bold green")
        if parent is not None:
            return parent.add(text)
        return Tree(text)

    def variables(self) -> Set[str]:
        return {self.name}

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("Variable", self.name))


# ============================================================================
# Unary Operations
# ============================================================================

class UnaryOp(Node):
    """Base class for unary operations and elementary single-argument functions."""

    def __init__(self, child: Node) -> None:
        self.child = _to_node(child)

    def variables(self) -> Set[str]:
        return self.child.variables()


class Negate(UnaryOp):
    """Negation node (-x)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return -self.child.evaluate(env)

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
            tracker.start_step(
                rule_name="Negation Rule",
                rule_formula=f"d/d{var}[ -u ] = -(u')",
                input_expr=self.to_infix(),
                target_var=var
            )
        
        d_child = self.child.differentiate(var, tracker)
        raw = Negate(d_child)
        sim = raw.simplify()
        
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def to_infix(self, parent_prec: int = 0) -> str:
        child_str = self.child.to_infix(self.PREC_NEG)
        res = f"-{child_str}"
        if parent_prec > self.PREC_NEG:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"-{self.child.to_latex()}"

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text("Negate (-)", style="bold yellow")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.child.to_rich_tree(tree)
        return tree

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Negate) and self.child == other.child

    def __hash__(self) -> int:
        return hash(("Negate", self.child))


# ============================================================================
# Binary Operations
# ============================================================================

class BinaryOp(Node):
    """Base class for binary operations."""

    def __init__(self, left: Node, right: Node) -> None:
        self.left = _to_node(left)
        self.right = _to_node(right)

    def variables(self) -> Set[str]:
        return self.left.variables() | self.right.variables()


class Add(BinaryOp):
    """Addition node (left + right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.left.evaluate(env) + self.right.evaluate(env)

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def to_infix(self, parent_prec: int = 0) -> str:
        left_str = self.left.to_infix(self.PREC_ADD)
        right_str = self.right.to_infix(self.PREC_ADD)
        res = f"{left_str} + {right_str}"
        if parent_prec > self.PREC_ADD:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{self.left.to_latex()} + {self.right.to_latex()}"

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text("Add (+)", style="bold gold1")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.left.to_rich_tree(tree)
        self.right.to_rich_tree(tree)
        return tree

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Add) and (
            (self.left == other.left and self.right == other.right) or
            (self.left == other.right and self.right == other.left)
        )

    def __hash__(self) -> int:
        return hash(("Add", frozenset([self.left, self.right])))


class Subtract(BinaryOp):
    """Subtraction node (left - right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.left.evaluate(env) - self.right.evaluate(env)

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def to_infix(self, parent_prec: int = 0) -> str:
        left_str = self.left.to_infix(self.PREC_SUB)
        # Right side needs higher precedence to parenthesize (a - (b + c))
        right_str = self.right.to_infix(self.PREC_SUB + 1)
        res = f"{left_str} - {right_str}"
        if parent_prec > self.PREC_SUB:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{self.left.to_latex()} - {self.right.to_latex()}"

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text("Subtract (-)", style="bold gold1")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.left.to_rich_tree(tree)
        self.right.to_rich_tree(tree)
        return tree

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Subtract) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("Subtract", self.left, self.right))


class Multiply(BinaryOp):
    """Multiplication node (left * right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        return self.left.evaluate(env) * self.right.evaluate(env)

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        # Check for constant multiple rule optimization
        if self.left.is_constant() and not self.right.is_constant():
            if tracker:
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
            if tracker:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        if self.right.is_constant() and not self.left.is_constant():
            if tracker:
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
            if tracker:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        if tracker:
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
        
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def to_infix(self, parent_prec: int = 0) -> str:
        left_str = self.left.to_infix(self.PREC_MUL)
        right_str = self.right.to_infix(self.PREC_MUL)
        res = f"{left_str} * {right_str}"
        if parent_prec > self.PREC_MUL:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{self.left.to_latex()} \\cdot {self.right.to_latex()}"

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text("Multiply (*)", style="bold dark_orange")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.left.to_rich_tree(tree)
        self.right.to_rich_tree(tree)
        return tree

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Multiply) and (
            (self.left == other.left and self.right == other.right) or
            (self.left == other.right and self.right == other.left)
        )

    def __hash__(self) -> int:
        return hash(("Multiply", frozenset([self.left, self.right])))


class Divide(BinaryOp):
    """Division node (left / right)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        denom = self.right.evaluate(env)
        if denom == 0:
            return float('nan')
        return self.left.evaluate(env) / denom

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        # Constant denominator specialization: (u / c)' = u' / c
        if self.right.is_constant() and not self.left.is_constant():
            if tracker:
                tracker.start_step(
                    rule_name="Constant Denominator Rule",
                    rule_formula=f"d/d{var}[ u / c ] = (u') / c",
                    input_expr=self.to_infix(),
                    target_var=var,
                    notes=f"c = {self.right.to_infix()}"
                )
            du = self.left.differentiate(var, tracker)
            raw = Divide(du, self.right)
            sim = raw.simplify()
            if tracker:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        if tracker:
            tracker.start_step(
                rule_name="Quotient Rule",
                rule_formula=f"d/d{var}[ u / v ] = (u' * v - u * v') / (v^2)",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"u = {self.left.to_infix()}, v = {self.right.to_infix()}"
            )
        
        du = self.left.differentiate(var, tracker)
        dv = self.right.differentiate(var, tracker)
        
        numerator = Subtract(Multiply(du, self.right), Multiply(self.left, dv))
        denominator = Power(self.right, Constant(2))
        raw = Divide(numerator, denominator)
        sim = raw.simplify()
        
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def to_infix(self, parent_prec: int = 0) -> str:
        left_str = self.left.to_infix(self.PREC_DIV)
        right_str = self.right.to_infix(self.PREC_DIV + 1)
        res = f"{left_str} / {right_str}"
        if parent_prec > self.PREC_DIV:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"\\frac{{{self.left.to_latex()}}}{{{self.right.to_latex()}}}"

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text("Divide (/)", style="bold dark_orange")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.left.to_rich_tree(tree)
        self.right.to_rich_tree(tree)
        return tree

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Divide) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("Divide", self.left, self.right))


class Power(BinaryOp):
    """Exponentiation node (base ^ exponent)."""

    def evaluate(self, env: Dict[str, float]) -> float:
        base_val = self.left.evaluate(env)
        exp_val = self.right.evaluate(env)
        try:
            return math.pow(base_val, exp_val)
        except (ValueError, OverflowError):
            return float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        base_has_var = var in self.left.variables()
        exp_has_var = var in self.right.variables()

        # Case 1: Both constant w.r.t var
        if not base_has_var and not exp_has_var:
            if tracker:
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
            if tracker:
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
            if tracker:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        # Case 3: Exponential Rule a^u(x) where a is constant
        if not base_has_var and exp_has_var:
            if tracker:
                tracker.start_step(
                    rule_name="Exponential Power Rule",
                    rule_formula=f"d/d{var}[ a^u ] = a^u * ln(a) * u'",
                    input_expr=self.to_infix(),
                    target_var=var,
                    notes=f"a = {self.left.to_infix()}, u = {self.right.to_infix()}"
                )
            
            dv = self.right.differentiate(var, tracker)
            # a^u * ln(a) * u'
            raw = Multiply(
                Multiply(self, Ln(self.left)),
                dv
            )
            sim = raw.simplify()
            if tracker:
                tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
            return raw

        # Case 4: General Power Rule u(x)^v(x)
        if tracker:
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
        
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def to_infix(self, parent_prec: int = 0) -> str:
        # Power is right associative
        left_str = self.left.to_infix(self.PREC_POW + 1)
        right_str = self.right.to_infix(self.PREC_POW)
        res = f"{left_str} ^ {right_str}"
        if parent_prec > self.PREC_POW:
            return f"({res})"
        return res

    def to_latex(self) -> str:
        return f"{{{self.left.to_latex()}}}^{{{self.right.to_latex()}}}"

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text("Power (^)", style="bold purple")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.left.to_rich_tree(tree)
        self.right.to_rich_tree(tree)
        return tree

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Power) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("Power", self.left, self.right))


# ============================================================================
# Elementary Functions (Trigonometric, Exponential, Logarithmic, etc.)
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

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text(f"{self.__class__.__name__}()", style="bold cyan")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.child.to_rich_tree(tree)
        return tree

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self.child == other.child

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.child))


class Sin(FunctionNode):
    func_name = "sin"
    latex_name = "sin"

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.sin(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Cos(FunctionNode):
    func_name = "cos"
    latex_name = "cos"

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.cos(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Tan(FunctionNode):
    func_name = "tan"
    latex_name = "tan"

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.tan(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Sec(FunctionNode):
    func_name = "sec"
    latex_name = "sec"

    def evaluate(self, env: Dict[str, float]) -> float:
        c = math.cos(self.child.evaluate(env))
        return 1.0 / c if c != 0 else float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Csc(FunctionNode):
    func_name = "csc"
    latex_name = "csc"

    def evaluate(self, env: Dict[str, float]) -> float:
        s = math.sin(self.child.evaluate(env))
        return 1.0 / s if s != 0 else float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Cot(FunctionNode):
    func_name = "cot"
    latex_name = "cot"

    def evaluate(self, env: Dict[str, float]) -> float:
        t = math.tan(self.child.evaluate(env))
        return 1.0 / t if t != 0 else float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Asin(FunctionNode):
    func_name = "asin"
    latex_name = "arcsin"

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.child.evaluate(env)
        return math.asin(val) if -1.0 <= val <= 1.0 else float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Acos(FunctionNode):
    func_name = "acos"
    latex_name = "arccos"

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.child.evaluate(env)
        return math.acos(val) if -1.0 <= val <= 1.0 else float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Atan(FunctionNode):
    func_name = "atan"
    latex_name = "arctan"

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.atan(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Sinh(FunctionNode):
    func_name = "sinh"
    latex_name = "sinh"

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.sinh(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
            tracker.start_step(
                rule_name="Chain Rule [sinh]",
                rule_formula=f"d/d{var}[ sinh(u) ] = cosh(u) * u'",
                input_expr=self.to_infix(),
                target_var=var
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Cosh(self.child), du)
        sim = raw.simplify()
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Cosh(FunctionNode):
    func_name = "cosh"
    latex_name = "cosh"

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.cosh(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
            tracker.start_step(
                rule_name="Chain Rule [cosh]",
                rule_formula=f"d/d{var}[ cosh(u) ] = sinh(u) * u'",
                input_expr=self.to_infix(),
                target_var=var
            )
        du = self.child.differentiate(var, tracker)
        raw = Multiply(Sinh(self.child), du)
        sim = raw.simplify()
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Tanh(FunctionNode):
    func_name = "tanh"
    latex_name = "tanh"

    def evaluate(self, env: Dict[str, float]) -> float:
        return math.tanh(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
            tracker.start_step(
                rule_name="Chain Rule [tanh]",
                rule_formula=f"d/d{var}[ tanh(u) ] = (1 - tanh(u)^2) * u'",
                input_expr=self.to_infix(),
                target_var=var
            )
        du = self.child.differentiate(var, tracker)
        # (1 - tanh(u)^2) * u'
        sech_sq = Subtract(Constant(1), Power(Tanh(self.child), Constant(2)))
        raw = Multiply(sech_sq, du)
        sim = raw.simplify()
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Exp(FunctionNode):
    func_name = "exp"
    latex_name = "exp"

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.child.evaluate(env)
        try:
            return math.exp(val)
        except OverflowError:
            return float('inf')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Ln(FunctionNode):
    """Natural logarithm node ln(x)."""
    func_name = "ln"
    latex_name = "ln"

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.child.evaluate(env)
        return math.log(val) if val > 0 else float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw


class Log(Node):
    """Logarithm with arbitrary base: log_base(x)."""

    def __init__(self, child: Node, base: Optional[Node] = None) -> None:
        self.child = _to_node(child)
        self.base = _to_node(base) if base is not None else Constant(10)

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.child.evaluate(env)
        base_val = self.base.evaluate(env)
        if val <= 0 or base_val <= 0 or base_val == 1.0:
            return float('nan')
        return math.log(val, base_val)

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
            tracker.start_step(
                rule_name="Chain Rule [log_b]",
                rule_formula=f"d/d{var}[ log_b(u) ] = u' / (u * ln(b))",
                input_expr=self.to_infix(),
                target_var=var,
                notes=f"b = {self.base.to_infix()}, u = {self.child.to_infix()}"
            )
        du = self.child.differentiate(var, tracker)
        # u' / (u * ln(b))
        denom = Multiply(self.child, Ln(self.base))
        raw = Divide(du, denom)
        sim = raw.simplify()
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def simplify(self) -> Node:
        from .simplifier import simplify
        return simplify(self)

    def to_infix(self, parent_prec: int = 0) -> str:
        if self.base == Constant(10):
            return f"log({self.child.to_infix()})"
        return f"log({self.child.to_infix()}, {self.base.to_infix()})"

    def to_latex(self) -> str:
        if self.base == Constant(10):
            return f"\\log\\left({self.child.to_latex()}\\right)"
        return f"\\log_{{{self.base.to_latex()}}}\\left({self.child.to_latex()}\\right)"

    def to_rich_tree(self, parent: Optional[Tree] = None) -> Tree:
        text = Text(f"Log(base={self.base})", style="bold cyan")
        tree = parent.add(text) if parent is not None else Tree(text)
        self.child.to_rich_tree(tree)
        return tree

    def variables(self) -> Set[str]:
        return self.child.variables() | self.base.variables()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Log) and self.child == other.child and self.base == other.base

    def __hash__(self) -> int:
        return hash(("Log", self.child, self.base))


class Sqrt(FunctionNode):
    func_name = "sqrt"
    latex_name = "sqrt"

    def evaluate(self, env: Dict[str, float]) -> float:
        val = self.child.evaluate(env)
        return math.sqrt(val) if val >= 0 else float('nan')

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_latex(self) -> str:
        return f"\\sqrt{{{self.child.to_latex()}}}"


class Abs(FunctionNode):
    func_name = "abs"
    latex_name = "abs"

    def evaluate(self, env: Dict[str, float]) -> float:
        return abs(self.child.evaluate(env))

    def differentiate(self, var: str, tracker: Optional[Any] = None) -> Node:
        if tracker:
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
        if tracker:
            tracker.end_step(raw_result=raw.to_infix(), simplified_result=sim.to_infix())
        return raw

    def to_infix(self, parent_prec: int = 0) -> str:
        return f"abs({self.child.to_infix(0)})"

    def to_latex(self) -> str:
        return f"\\left|{self.child.to_latex()}\\right|"
