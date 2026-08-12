"""
Abstract Syntax Tree node definitions for the Symbolic Calculus Engine.

Every node implements:
  - differentiate(var): symbolic derivative via calculus rules
  - simplify(): bottom-up algebraic simplification
  - deep_simplify(): multi-pass simplification until stable
  - evaluate(env): numerical evaluation given variable bindings
  - tree_lines(): ASCII tree rendering for the TUI
"""
import math


# ═══════════════════════════════════════════════════════════════
#  Base Class
# ═══════════════════════════════════════════════════════════════

class Expr:
    """Base class for all AST expression nodes."""

    def differentiate(self, var: str) -> "Expr":
        """Return the symbolic derivative with respect to var."""
        raise NotImplementedError(f"{type(self).__name__}.differentiate()")

    def simplify(self) -> "Expr":
        """Single-pass bottom-up simplification."""
        return self

    def deep_simplify(self, max_passes: int = 10) -> "Expr":
        """Repeatedly simplify until no further changes occur."""
        current = self
        for _ in range(max_passes):
            simplified = current.simplify()
            if str(simplified) == str(current):
                return simplified
            current = simplified
        return current

    def evaluate(self, env: dict) -> float:
        """Numerically evaluate with variable bindings like {'x': 3.0}."""
        raise NotImplementedError(f"{type(self).__name__}.evaluate()")

    def __repr__(self) -> str:
        return str(self)

    def tree_lines(self, prefix: str = "", is_last: bool = True,
                   is_root: bool = False) -> list:
        """Render this node as an ASCII tree, returning a list of lines."""
        connector = "" if is_root else ("└── " if is_last else "├── ")
        return [prefix + connector + str(self)]


# ═══════════════════════════════════════════════════════════════
#  Leaf Nodes
# ═══════════════════════════════════════════════════════════════

class Const(Expr):
    """A numeric constant."""
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = float(value)

    def differentiate(self, var):
        return Const(0)

    def evaluate(self, env):
        return self.value

    def __str__(self):
        v = self.value
        if v != v:                 # NaN
            return "NaN"
        if abs(v) == float("inf"):
            return "∞" if v > 0 else "-∞"
        if isinstance(v, float) and v.is_integer() and abs(v) < 1e15:
            return str(int(v))
        return str(v)

    def tree_lines(self, prefix="", is_last=True, is_root=False):
        connector = "" if is_root else ("└── " if is_last else "├── ")
        return [prefix + connector + str(self)]


class Var(Expr):
    """A symbolic variable."""
    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def differentiate(self, var):
        return Const(1) if self.name == var else Const(0)

    def evaluate(self, env):
        if self.name in env:
            return float(env[self.name])
        raise ValueError(f"Undefined variable: '{self.name}'")

    def __str__(self):
        return self.name

    def tree_lines(self, prefix="", is_last=True, is_root=False):
        connector = "" if is_root else ("└── " if is_last else "├── ")
        return [prefix + connector + self.name]


# ═══════════════════════════════════════════════════════════════
#  Binary Operators
# ═══════════════════════════════════════════════════════════════

class _BinOp(Expr):
    """Abstract base for binary operations (shared tree rendering)."""
    symbol = "?"
    __slots__ = ("left", "right")

    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def tree_lines(self, prefix="", is_last=True, is_root=False):
        connector = "" if is_root else ("└── " if is_last else "├── ")
        extension = "" if is_root else ("    " if is_last else "│   ")
        lines = [prefix + connector + self.symbol]
        lines.extend(self.left.tree_lines(prefix + extension, False))
        lines.extend(self.right.tree_lines(prefix + extension, True))
        return lines


class Add(_BinOp):
    symbol = "+"

    def differentiate(self, var):
        return Add(self.left.differentiate(var), self.right.differentiate(var))

    def simplify(self):
        l, r = self.left.simplify(), self.right.simplify()
        if isinstance(l, Const) and isinstance(r, Const):
            return Const(l.value + r.value)
        if isinstance(l, Const) and l.value == 0:
            return r
        if isinstance(r, Const) and r.value == 0:
            return l
        return Add(l, r)

    def evaluate(self, env):
        return self.left.evaluate(env) + self.right.evaluate(env)

    def __str__(self):
        return f"({self.left} + {self.right})"


class Sub(_BinOp):
    symbol = "−"

    def differentiate(self, var):
        return Sub(self.left.differentiate(var), self.right.differentiate(var))

    def simplify(self):
        l, r = self.left.simplify(), self.right.simplify()
        if isinstance(l, Const) and isinstance(r, Const):
            return Const(l.value - r.value)
        if isinstance(r, Const) and r.value == 0:
            return l
        if isinstance(l, Const) and l.value == 0:
            return Mul(Const(-1), r)   # 0 - r  →  -r
        if str(l) == str(r):
            return Const(0)
        return Sub(l, r)

    def evaluate(self, env):
        return self.left.evaluate(env) - self.right.evaluate(env)

    def __str__(self):
        return f"({self.left} - {self.right})"


class Mul(_BinOp):
    symbol = "×"

    def differentiate(self, var):
        # Product rule: (uv)' = u'v + uv'
        return Add(
            Mul(self.left.differentiate(var), self.right),
            Mul(self.left, self.right.differentiate(var)),
        )

    def simplify(self):
        l, r = self.left.simplify(), self.right.simplify()
        if isinstance(l, Const) and isinstance(r, Const):
            return Const(l.value * r.value)
        if isinstance(l, Const):
            if l.value == 0:
                return Const(0)
            if l.value == 1:
                return r
        if isinstance(r, Const):
            if r.value == 0:
                return Const(0)
            if r.value == 1:
                return l
        return Mul(l, r)

    def evaluate(self, env):
        return self.left.evaluate(env) * self.right.evaluate(env)

    def __str__(self):
        # Display -1 * expr as (-expr) for readability
        if isinstance(self.left, Const) and self.left.value == -1:
            return f"(-{self.right})"
        return f"({self.left} * {self.right})"


class Div(_BinOp):
    symbol = "÷"

    def differentiate(self, var):
        # Quotient rule: (u/v)' = (u'v − uv') / v²
        return Div(
            Sub(
                Mul(self.left.differentiate(var), self.right),
                Mul(self.left, self.right.differentiate(var)),
            ),
            Pow(self.right, Const(2)),
        )

    def simplify(self):
        l, r = self.left.simplify(), self.right.simplify()
        if isinstance(l, Const) and isinstance(r, Const) and r.value != 0:
            return Const(l.value / r.value)
        if isinstance(l, Const) and l.value == 0:
            return Const(0)
        if isinstance(r, Const) and r.value == 1:
            return l
        if str(l) == str(r):
            return Const(1)
        return Div(l, r)

    def evaluate(self, env):
        d = self.right.evaluate(env)
        if d == 0:
            n = self.left.evaluate(env)
            return float("inf") if n >= 0 else float("-inf")
        return self.left.evaluate(env) / d

    def __str__(self):
        return f"({self.left} / {self.right})"


class Pow(_BinOp):
    symbol = "^"

    def differentiate(self, var):
        if isinstance(self.right, Const):
            # Power rule: d/dx[u^n] = n · u^(n−1) · u'
            n = self.right
            return Mul(
                Mul(n, Pow(self.left, Const(n.value - 1))),
                self.left.differentiate(var),
            )
        # General: d/dx[u^v] = u^v · (v'·ln(u) + v·u'/u)
        return Mul(
            self,
            Add(
                Mul(self.right.differentiate(var), Ln(self.left)),
                Mul(self.right, Div(self.left.differentiate(var), self.left)),
            ),
        )

    def simplify(self):
        base, exp = self.left.simplify(), self.right.simplify()
        if isinstance(base, Const) and isinstance(exp, Const):
            try:
                result = base.value ** exp.value
                if isinstance(result, complex):
                    return Pow(base, exp)
                return Const(result)
            except (ValueError, OverflowError):
                return Pow(base, exp)
        if isinstance(exp, Const):
            if exp.value == 0:
                return Const(1)
            if exp.value == 1:
                return base
        if isinstance(base, Const):
            if base.value == 0:
                return Const(0)
            if base.value == 1:
                return Const(1)
        return Pow(base, exp)

    def evaluate(self, env):
        try:
            result = self.left.evaluate(env) ** self.right.evaluate(env)
            if isinstance(result, complex):
                return float("nan")
            return result
        except (ValueError, OverflowError):
            return float("nan")

    def __str__(self):
        return f"({self.left} ^ {self.right})"


# ═══════════════════════════════════════════════════════════════
#  Unary Functions (with chain rule support)
# ═══════════════════════════════════════════════════════════════

class _UnaryFunc(Expr):
    """Abstract base for single-argument mathematical functions."""
    func_name = "?"
    __slots__ = ("arg",)

    def __init__(self, arg: Expr):
        self.arg = arg

    def __str__(self):
        return f"{self.func_name}({self.arg})"

    def tree_lines(self, prefix="", is_last=True, is_root=False):
        connector = "" if is_root else ("└── " if is_last else "├── ")
        extension = "" if is_root else ("    " if is_last else "│   ")
        lines = [prefix + connector + self.func_name]
        lines.extend(self.arg.tree_lines(prefix + extension, True))
        return lines


class Sin(_UnaryFunc):
    func_name = "sin"

    def differentiate(self, var):
        # Chain rule: d/dx[sin(u)] = cos(u) · u'
        return Mul(Cos(self.arg), self.arg.differentiate(var))

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const):
            return Const(math.sin(a.value))
        return Sin(a)

    def evaluate(self, env):
        return math.sin(self.arg.evaluate(env))


class Cos(_UnaryFunc):
    func_name = "cos"

    def differentiate(self, var):
        # Chain rule: d/dx[cos(u)] = −sin(u) · u'
        return Mul(Mul(Const(-1), Sin(self.arg)), self.arg.differentiate(var))

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const):
            return Const(math.cos(a.value))
        return Cos(a)

    def evaluate(self, env):
        return math.cos(self.arg.evaluate(env))


class Tan(_UnaryFunc):
    func_name = "tan"

    def differentiate(self, var):
        # Chain rule: d/dx[tan(u)] = sec²(u) · u'  =  (1/cos²(u)) · u'
        return Mul(
            Div(Const(1), Pow(Cos(self.arg), Const(2))),
            self.arg.differentiate(var),
        )

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const):
            try:
                return Const(math.tan(a.value))
            except ValueError:
                pass
        return Tan(a)

    def evaluate(self, env):
        return math.tan(self.arg.evaluate(env))


class Ln(_UnaryFunc):
    func_name = "ln"

    def differentiate(self, var):
        # Chain rule: d/dx[ln(u)] = u' / u
        return Mul(Div(Const(1), self.arg), self.arg.differentiate(var))

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const) and a.value > 0:
            return Const(math.log(a.value))
        return Ln(a)

    def evaluate(self, env):
        val = self.arg.evaluate(env)
        if val <= 0:
            return float("nan")
        return math.log(val)


class Exp(_UnaryFunc):
    func_name = "exp"

    def differentiate(self, var):
        # Chain rule: d/dx[exp(u)] = exp(u) · u'
        return Mul(Exp(self.arg), self.arg.differentiate(var))

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const):
            try:
                return Const(math.exp(a.value))
            except OverflowError:
                pass
        return Exp(a)

    def evaluate(self, env):
        try:
            return math.exp(self.arg.evaluate(env))
        except OverflowError:
            return float("inf")


class Sqrt(_UnaryFunc):
    func_name = "sqrt"

    def differentiate(self, var):
        # Chain rule: d/dx[sqrt(u)] = u' / (2 · sqrt(u))
        return Mul(
            Div(Const(1), Mul(Const(2), Sqrt(self.arg))),
            self.arg.differentiate(var),
        )

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const) and a.value >= 0:
            return Const(math.sqrt(a.value))
        return Sqrt(a)

    def evaluate(self, env):
        val = self.arg.evaluate(env)
        if val < 0:
            return float("nan")
        return math.sqrt(val)


class Asin(_UnaryFunc):
    func_name = "asin"

    def differentiate(self, var):
        # Chain rule: d/dx[asin(u)] = u' / sqrt(1 − u²)
        return Mul(
            Div(Const(1), Sqrt(Sub(Const(1), Pow(self.arg, Const(2))))),
            self.arg.differentiate(var),
        )

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const) and -1 <= a.value <= 1:
            return Const(math.asin(a.value))
        return Asin(a)

    def evaluate(self, env):
        return math.asin(self.arg.evaluate(env))


class Acos(_UnaryFunc):
    func_name = "acos"

    def differentiate(self, var):
        # Chain rule: d/dx[acos(u)] = −u' / sqrt(1 − u²)
        return Mul(
            Mul(Const(-1), Div(Const(1), Sqrt(Sub(Const(1), Pow(self.arg, Const(2)))))),
            self.arg.differentiate(var),
        )

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const) and -1 <= a.value <= 1:
            return Const(math.acos(a.value))
        return Acos(a)

    def evaluate(self, env):
        return math.acos(self.arg.evaluate(env))


class Atan(_UnaryFunc):
    func_name = "atan"

    def differentiate(self, var):
        # Chain rule: d/dx[atan(u)] = u' / (1 + u²)
        return Mul(
            Div(Const(1), Add(Const(1), Pow(self.arg, Const(2)))),
            self.arg.differentiate(var),
        )

    def simplify(self):
        a = self.arg.simplify()
        if isinstance(a, Const):
            return Const(math.atan(a.value))
        return Atan(a)

    def evaluate(self, env):
        return math.atan(self.arg.evaluate(env))
