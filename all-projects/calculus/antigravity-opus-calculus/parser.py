"""
Recursive descent parser for mathematical expressions.

Grammar (implements standard PEMDAS precedence):
  expr   → term (('+' | '-') term)*
  term   → power (('*' | '/') power)*
  power  → unary ('^' power)?          # right-associative
  unary  → '-' unary | call
  call   → FUNC '(' expr ')' | atom
  atom   → NUMBER | VAR | '(' expr ')'

Features:
  - Implicit multiplication: 2x, 2sin(x), 2(x+1), (x+1)(x-1)
  - Built-in constants: pi → π, e → Euler's number
  - Functions: sin, cos, tan, ln, exp
"""
import math

try:
    from .nodes import (Const, Var, Add, Sub, Mul, Div, Pow,
                        Sin, Cos, Tan, Ln, Exp)
except ImportError:
    from nodes import (Const, Var, Add, Sub, Mul, Div, Pow,
                       Sin, Cos, Tan, Ln, Exp)


# ── Exceptions ───────────────────────────────────────────────

class ParseError(Exception):
    """Raised when an expression cannot be parsed."""
    pass


# ── Constants & Recognized Functions ─────────────────────────

FUNCTIONS = {"sin", "cos", "tan", "ln", "exp"}
CONSTANTS = {"pi": math.pi, "e": math.e}


# ── Tokenizer ────────────────────────────────────────────────

def _tokenize(text: str) -> list:
    """Convert raw input into a list of (type, value) tokens."""
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # Operators and parentheses
        if ch in "+-*/^()":
            tokens.append(("OP", ch))
            i += 1
            continue

        # Numeric literal (integer or decimal)
        if ch.isdigit() or ch == ".":
            j = i
            dot = ch == "."
            j += 1
            while j < len(text) and (text[j].isdigit() or (text[j] == "." and not dot)):
                if text[j] == ".":
                    dot = True
                j += 1
            tokens.append(("NUM", text[i:j]))
            i = j
            continue

        # Identifier: function name, constant, or variable
        if ch.isalpha() or ch == "_":
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            word = text[i:j]
            if word in FUNCTIONS:
                tokens.append(("FUNC", word))
            elif word in CONSTANTS:
                tokens.append(("NUM", str(CONSTANTS[word])))
            else:
                tokens.append(("VAR", word))
            i = j
            continue

        raise ParseError(f"Unexpected character: {ch!r}")

    return tokens


def _insert_implicit_mul(tokens: list) -> list:
    """Insert '*' tokens where multiplication is implied.

    Examples: 2x → 2*x, 2sin(x) → 2*sin(x), (a)(b) → (a)*(b)
    """
    result = []
    for i, tok in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            left_ok = prev[0] in ("NUM", "VAR") or prev[1] == ")"
            right_ok = tok[0] in ("NUM", "VAR", "FUNC") or tok[1] == "("
            if left_ok and right_ok:
                result.append(("OP", "*"))
        result.append(tok)
    return result


# ── Parser ───────────────────────────────────────────────────

class _Parser:
    """Recursive descent parser producing an AST from token list."""

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    # -- helpers --

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _consume(self):
        tok = self._peek()
        if tok is None:
            raise ParseError("Unexpected end of expression")
        self.pos += 1
        return tok

    def _expect(self, kind: str, value: str = None):
        tok = self._consume()
        if tok[0] != kind or (value is not None and tok[1] != value):
            expected = f"{kind}({value})" if value else kind
            raise ParseError(
                f"Expected {expected}, got {tok[0]}({tok[1]!r})")
        return tok

    # -- grammar rules --

    def parse(self):
        result = self._expr()
        if self.pos < len(self.tokens):
            raise ParseError(
                f"Unexpected token: {self.tokens[self.pos][1]!r}")
        return result

    def _expr(self):
        """expr → term (('+' | '-') term)*"""
        node = self._term()
        while self._peek() and self._peek()[1] in ("+", "-"):
            op = self._consume()[1]
            right = self._term()
            node = Add(node, right) if op == "+" else Sub(node, right)
        return node

    def _term(self):
        """term → power (('*' | '/') power)*"""
        node = self._power()
        while self._peek() and self._peek()[1] in ("*", "/"):
            op = self._consume()[1]
            right = self._power()
            node = Mul(node, right) if op == "*" else Div(node, right)
        return node

    def _power(self):
        """power → unary ('^' power)?  — right-associative"""
        node = self._unary()
        if self._peek() and self._peek()[1] == "^":
            self._consume()
            right = self._power()        # recurse for right-assoc
            node = Pow(node, right)
        return node

    def _unary(self):
        """unary → '-' unary | call"""
        if self._peek() and self._peek()[1] == "-":
            self._consume()
            operand = self._unary()
            return Mul(Const(-1), operand)
        return self._call()

    def _call(self):
        """call → FUNC '(' expr ')' | atom"""
        if self._peek() and self._peek()[0] == "FUNC":
            name = self._consume()[1]
            self._expect("OP", "(")
            arg = self._expr()
            self._expect("OP", ")")
            func_map = {
                "sin": Sin, "cos": Cos, "tan": Tan,
                "ln": Ln, "exp": Exp,
            }
            return func_map[name](arg)
        return self._atom()

    def _atom(self):
        """atom → NUMBER | VAR | '(' expr ')'"""
        tok = self._peek()
        if tok is None:
            raise ParseError("Unexpected end of expression")
        if tok[0] == "NUM":
            self._consume()
            return Const(float(tok[1]))
        if tok[0] == "VAR":
            self._consume()
            return Var(tok[1])
        if tok[1] == "(":
            self._consume()
            node = self._expr()
            self._expect("OP", ")")
            return node
        raise ParseError(f"Unexpected: {tok[1]!r}")


# ── Public API ───────────────────────────────────────────────

def parse(text: str):
    """Parse a mathematical expression string into an AST.

    >>> from nodes import *
    >>> ast = parse("x^2 * sin(x)")
    >>> str(ast)
    '((x ^ 2) * sin(x))'
    """
    text = text.strip()
    if not text:
        raise ParseError("Empty expression")
    tokens = _tokenize(text)
    tokens = _insert_implicit_mul(tokens)
    return _Parser(tokens).parse()
