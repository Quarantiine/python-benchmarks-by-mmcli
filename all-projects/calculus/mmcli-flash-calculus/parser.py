"""
Expression Lexer and Parser for symbolic math string representations.

Supports standard mathematical infix notation with operator precedence:
+, -, *, /, ^ (or **), functions (sin, cos, tan, exp, ln, sqrt, abs),
implicit multiplication (e.g., 2x, 3(x+1)), and parenthesized expressions.
"""

import re
from typing import List, Tuple, Optional
from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Exp, Ln, Sqrt, Abs, E_CONST, PI_CONST
)

# Token types
TOKEN_NUMBER = "NUMBER"
TOKEN_IDENT = "IDENT"
TOKEN_PLUS = "PLUS"
TOKEN_MINUS = "MINUS"
TOKEN_MUL = "MUL"
TOKEN_DIV = "DIV"
TOKEN_POW = "POW"
TOKEN_LPAREN = "LPAREN"
TOKEN_RPAREN = "RPAREN"
TOKEN_COMMA = "COMMA"

KNOWN_FUNCTIONS = {"sin": Sin, "cos": Cos, "tan": Tan, "exp": Exp, "ln": Ln, "log": Ln, "sqrt": Sqrt, "abs": Abs}

class Token:
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r})"


def tokenize(expr_str: str) -> List[Token]:
    """Convert input math string into a list of Tokens."""
    token_specification = [
        (TOKEN_NUMBER, r'\d+(?:\.\d+)?(?:[eE][+-]?\d+)?'),
        (TOKEN_IDENT,  r'[a-zA-Z_][a-zA-Z0-9_]*'),
        (TOKEN_POW,    r'\*\*|\^'),
        (TOKEN_PLUS,   r'\+'),
        (TOKEN_MINUS,  r'-'),
        (TOKEN_MUL,    r'\*'),
        (TOKEN_DIV,    r'/'),
        (TOKEN_LPAREN, r'\('),
        (TOKEN_RPAREN, r'\)'),
        (TOKEN_COMMA,  r','),
        ('SKIP',       r'[ \t\n\r]+'),
        ('MISMATCH',   r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    raw_tokens: List[Token] = []
    
    for mo in re.finditer(tok_regex, expr_str):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise ValueError(f"Unexpected character {value!r} in expression: {expr_str}")
        else:
            raw_tokens.append(Token(kind, value))
            
    # Insert implicit multiplication tokens where needed (e.g. 2x -> 2*x, 3(x) -> 3*(x), x y -> x*y)
    tokens: List[Token] = []
    for i in range(len(raw_tokens)):
        t1 = raw_tokens[i]
        tokens.append(t1)
        if i + 1 < len(raw_tokens):
            t2 = raw_tokens[i + 1]
            # Cases for implicit multiplication:
            # NUMBER followed by IDENT or LPAREN (e.g., 2x, 2(x+1))
            # RPAREN followed by IDENT, NUMBER, or LPAREN (e.g., (a+b)2, (a+b)(c+d))
            # IDENT (not function) followed by IDENT, NUMBER, or LPAREN (e.g., x y, x 2, x(y))
            if t1.type == TOKEN_NUMBER and t2.type in (TOKEN_IDENT, TOKEN_LPAREN):
                tokens.append(Token(TOKEN_MUL, "*"))
            elif t1.type == TOKEN_RPAREN and t2.type in (TOKEN_IDENT, TOKEN_NUMBER, TOKEN_LPAREN):
                tokens.append(Token(TOKEN_MUL, "*"))
            elif t1.type == TOKEN_IDENT and t1.value.lower() not in KNOWN_FUNCTIONS:
                if t2.type in (TOKEN_IDENT, TOKEN_NUMBER, TOKEN_LPAREN):
                    tokens.append(Token(TOKEN_MUL, "*"))

    return tokens


class Parser:
    """Recursive descent parser with precedence climbing."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type: Optional[str] = None) -> Token:
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression.")
        if expected_type is not None and tok.type != expected_type:
            raise ValueError(f"Expected token {expected_type}, got {tok.type} ({tok.value!r})")
        self.pos += 1
        return tok

    def parse(self) -> Expr:
        expr = self.parse_expr(min_prec=0)
        if self.pos < len(self.tokens):
            tok = self.peek()
            raise ValueError(f"Unparsed token remaining: {tok.value if tok else ''}")
        return expr

    def parse_expr(self, min_prec: int = 0) -> Expr:
        left = self.parse_prefix()

        while True:
            tok = self.peek()
            if tok is None:
                break

            prec, is_right_assoc = self.get_infix_precedence(tok.type)
            if prec < min_prec:
                break

            self.consume()  # Consume binary operator token
            next_min_prec = prec if is_right_assoc else prec + 1
            right = self.parse_expr(next_min_prec)

            if tok.type == TOKEN_PLUS:
                left = Add(left, right)
            elif tok.type == TOKEN_MINUS:
                left = Sub(left, right)
            elif tok.type == TOKEN_MUL:
                left = Mul(left, right)
            elif tok.type == TOKEN_DIV:
                left = Div(left, right)
            elif tok.type == TOKEN_POW:
                left = Pow(left, right)

        return left

    def parse_prefix(self) -> Expr:
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of input when parsing expression.")

        if tok.type == TOKEN_MINUS:
            self.consume()
            # Unary minus precedence is high (e.g. 3)
            operand = self.parse_expr(min_prec=3)
            return Neg(operand)

        if tok.type == TOKEN_PLUS:
            self.consume()
            return self.parse_expr(min_prec=3)

        if tok.type == TOKEN_NUMBER:
            self.consume()
            try:
                if '.' in tok.value or 'e' in tok.value.lower():
                    val = float(tok.value)
                    if val.is_integer():
                        return Const(int(val))
                    return Const(val)
                else:
                    return Const(int(tok.value))
            except OverflowError:
                raise ValueError(f"Numeric literal value too large: {tok.value!r}")
            except ValueError:
                raise ValueError(f"Invalid numeric literal: {tok.value!r}")

        if tok.type == TOKEN_IDENT:
            self.consume()
            name = tok.value
            lower_name = name.lower()

            # Check if function call
            if lower_name in KNOWN_FUNCTIONS:
                func_cls = KNOWN_FUNCTIONS[lower_name]
                self.consume(TOKEN_LPAREN)
                arg = self.parse_expr(min_prec=0)
                self.consume(TOKEN_RPAREN)
                return func_cls(arg)

            if lower_name == "e":
                return Symbol("e")
            if lower_name == "pi":
                return Symbol("pi")

            return Symbol(name)

        if tok.type == TOKEN_LPAREN:
            self.consume(TOKEN_LPAREN)
            expr = self.parse_expr(min_prec=0)
            self.consume(TOKEN_RPAREN)
            return expr

        raise ValueError(f"Unexpected token: {tok.type} ({tok.value!r})")

    def get_infix_precedence(self, token_type: str) -> Tuple[int, bool]:
        """Returns (precedence, is_right_associative) for infix operators."""
        if token_type in (TOKEN_PLUS, TOKEN_MINUS):
            return (1, False)
        if token_type in (TOKEN_MUL, TOKEN_DIV):
            return (2, False)
        if token_type == TOKEN_POW:
            return (4, True)  # Exponentiation is right-associative
        return (-1, False)


def parse(expr_str: str) -> Expr:
    """Parse a mathematical expression string into an AST Expr object."""
    tokens = tokenize(expr_str)
    if not tokens:
        raise ValueError("Cannot parse empty expression.")
    parser = Parser(tokens)
    return parser.parse()