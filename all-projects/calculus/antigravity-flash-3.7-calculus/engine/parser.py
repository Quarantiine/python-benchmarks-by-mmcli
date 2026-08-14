"""
Mathematical Expression Parser (Pratt / Operator-Precedence)
=============================================================
Converts mathematical string expressions into AST Node trees with support
for operator precedence, implicit multiplication, functions, and named constants.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
import re
from typing import Callable, Dict, List, Optional, Set
from .ast_nodes import (
    Node, Constant, Variable, NamedConstant,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Sec, Csc, Cot,
    Asin, Acos, Atan, Sinh, Cosh, Tanh,
    Exp, Ln, Log, Sqrt, Abs,
    E, PI
)


class TokenType(Enum):
    NUMBER = auto()
    IDENT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    pos: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', pos={self.pos})"


class ParseError(Exception):
    def __init__(self, message: str, expr: str = "", pos: int = -1) -> None:
        self.message = message
        self.expr = expr
        self.pos = pos
        super().__init__(self._format())

    def _format(self) -> str:
        if self.pos >= 0 and self.expr:
            pointer = " " * self.pos + "^"
            return f"Parse Error at position {self.pos}:\n  {self.expr}\n  {pointer}\n{self.message}"
        return f"Parse Error: {self.message}"


def _is_ascii_alpha(ch: str) -> bool:
    return ('a' <= ch <= 'z') or ('A' <= ch <= 'Z') or ch == '_'


def _is_ascii_alnum(ch: str) -> bool:
    return _is_ascii_alpha(ch) or ('0' <= ch <= '9')


def _is_ascii_digit(ch: str) -> bool:
    return '0' <= ch <= '9'


class Lexer:
    """Tokenizes raw mathematical strings."""

    SUPERSCRIPTS = {
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
        '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    }

    FUNCTION_PREFIXES = (
        "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
        "asin", "acos", "atan", "sqrt", "sec", "csc", "cot",
        "sin", "cos", "tan", "exp", "log", "abs", "ln"
    )

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.length = len(text)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < self.length:
            ch = self.text[self.pos]

            if ch.isspace():
                self.pos += 1
                continue

            start_pos = self.pos

            # Unicode superscripts (e.g. x², x³)
            if ch in self.SUPERSCRIPTS or ch in ('⁺', '⁻'):
                tokens.append(Token(TokenType.CARET, "^", start_pos))
                is_neg = False
                if ch == '⁻':
                    is_neg = True
                    self.pos += 1
                elif ch == '⁺':
                    self.pos += 1
                
                super_digits = []
                while self.pos < self.length and self.text[self.pos] in self.SUPERSCRIPTS:
                    super_digits.append(self.SUPERSCRIPTS[self.text[self.pos]])
                    self.pos += 1
                
                num_str = "".join(super_digits) if super_digits else "1"
                if is_neg:
                    tokens.append(Token(TokenType.LPAREN, "(", start_pos))
                    tokens.append(Token(TokenType.MINUS, "-", start_pos))
                    tokens.append(Token(TokenType.NUMBER, num_str, start_pos))
                    tokens.append(Token(TokenType.RPAREN, ")", start_pos))
                else:
                    tokens.append(Token(TokenType.NUMBER, num_str, start_pos))
                continue

            # Numbers (integer, decimal, scientific notation)
            if _is_ascii_digit(ch) or (ch == '.' and self._peek_digit()):
                num_str = self._read_number()
                tokens.append(Token(TokenType.NUMBER, num_str, start_pos))
                continue

            # Identifiers & function names (e.g. sin, cos, x, theta, pi, cos3x)
            if _is_ascii_alpha(ch):
                ident_str = self._read_ident()
                tokens.append(Token(TokenType.IDENT, ident_str, start_pos))
                continue

            # Operators
            if ch == '+':
                tokens.append(Token(TokenType.PLUS, "+", start_pos))
                self.pos += 1
            elif ch == '-':
                tokens.append(Token(TokenType.MINUS, "-", start_pos))
                self.pos += 1
            elif ch == '*':
                if self.pos + 1 < self.length and self.text[self.pos + 1] == '*':
                    tokens.append(Token(TokenType.CARET, "^", start_pos))
                    self.pos += 2
                else:
                    tokens.append(Token(TokenType.STAR, "*", start_pos))
                    self.pos += 1
            elif ch == '/':
                tokens.append(Token(TokenType.SLASH, "/", start_pos))
                self.pos += 1
            elif ch == '^':
                tokens.append(Token(TokenType.CARET, "^", start_pos))
                self.pos += 1
            elif ch == '(':
                tokens.append(Token(TokenType.LPAREN, "(", start_pos))
                self.pos += 1
            elif ch == ')':
                tokens.append(Token(TokenType.RPAREN, ")", start_pos))
                self.pos += 1
            elif ch == ',':
                tokens.append(Token(TokenType.COMMA, ",", start_pos))
                self.pos += 1
            else:
                raise ParseError(f"Unexpected character '{ch}'", self.text, start_pos)

        tokens.append(Token(TokenType.EOF, "", self.pos))
        return tokens

    def _peek_digit(self) -> bool:
        if self.pos + 1 < self.length:
            return _is_ascii_digit(self.text[self.pos + 1])
        return False

    def _read_number(self) -> str:
        start = self.pos
        has_dot = False
        while self.pos < self.length:
            ch = self.text[self.pos]
            if _is_ascii_digit(ch):
                self.pos += 1
            elif ch == '.' and not has_dot:
                has_dot = True
                self.pos += 1
            elif ch in ('e', 'E') and self.pos + 1 < self.length:
                # Scientific notation
                next_ch = self.text[self.pos + 1]
                if _is_ascii_digit(next_ch) or next_ch in ('+', '-'):
                    self.pos += 2
                    while self.pos < self.length and _is_ascii_digit(self.text[self.pos]):
                        self.pos += 1
                break
            else:
                break
        return self.text[start:self.pos]

    def _read_ident(self) -> str:
        start = self.pos
        # Check if text at pos starts with a known function prefix followed by digits or variables
        for fn in self.FUNCTION_PREFIXES:
            fn_len = len(fn)
            if self.text[self.pos:self.pos + fn_len].lower() == fn:
                if self.pos + fn_len < self.length:
                    next_c = self.text[self.pos + fn_len]
                    if _is_ascii_alnum(next_c):
                        self.pos += fn_len
                        return fn
                else:
                    self.pos += fn_len
                    return fn

        while self.pos < self.length and _is_ascii_alnum(self.text[self.pos]):
            self.pos += 1
        return self.text[start:self.pos]


class Parser:
    """
    Pratt / Operator Precedence Parser with implicit multiplication support.
    """

    PREC_LOWEST = 0
    PREC_ADD = 10
    PREC_MUL = 20
    PREC_IMPLICIT_MUL = 25
    PREC_PREFIX = 30
    PREC_POWER = 40

    FUNCTIONS: Dict[str, Callable[..., Node]] = {
        "sin": Sin,
        "cos": Cos,
        "tan": Tan,
        "sec": Sec,
        "csc": Csc,
        "cot": Cot,
        "asin": Asin,
        "arcsin": Asin,
        "acos": Acos,
        "arccos": Acos,
        "atan": Atan,
        "arctan": Atan,
        "sinh": Sinh,
        "cosh": Cosh,
        "tanh": Tanh,
        "exp": Exp,
        "ln": Ln,
        "log": lambda x, base=None: Log(x, base) if base else Log(x, Constant(10)),
        "sqrt": Sqrt,
        "abs": Abs,
    }

    NAMED_CONSTANTS: Dict[str, Node] = {
        "e": E,
        "pi": PI,
        "tau": NamedConstant("tau", 6.283185307179586, "\\tau"),
        "phi": NamedConstant("phi", 1.618033988749895, "\\phi"),
    }

    def __init__(self, text: str) -> None:
        self.text = text
        self.tokens = Lexer(text).tokenize()
        self.curr_idx = 0

    def parse(self) -> Node:
        if self._peek().type == TokenType.EOF:
            raise ParseError("Empty expression", self.text, 0)
        node = self._parse_expr(self.PREC_LOWEST)
        if self._peek().type != TokenType.EOF:
            curr = self._peek()
            raise ParseError(f"Unexpected token '{curr.value}' after expression", self.text, curr.pos)
        return node

    def _peek(self) -> Token:
        return self.tokens[self.curr_idx]

    def _advance(self) -> Token:
        tok = self._peek()
        if tok.type != TokenType.EOF:
            self.curr_idx += 1
        return tok

    def _consume(self, expected_type: TokenType, msg: str = "") -> Token:
        tok = self._peek()
        if tok.type != expected_type:
            err_msg = msg or f"Expected {expected_type.name}, found '{tok.value}'"
            raise ParseError(err_msg, self.text, tok.pos)
        return self._advance()

    def _parse_expr(self, precedence: int) -> Node:
        left = self._parse_prefix()

        while True:
            # Check for implicit multiplication:
            # If next token can start an expression (e.g. NUMBER, IDENT, LPAREN),
            # treat as implicit multiplication!
            next_tok = self._peek()
            if self._can_start_prefix(next_tok):
                if precedence >= self.PREC_IMPLICIT_MUL:
                    break
                # Implicit multiplication
                right = self._parse_expr(self.PREC_IMPLICIT_MUL)
                left = Multiply(left, right)
                continue

            infix_prec = self._get_infix_precedence(next_tok.type)
            if precedence >= infix_prec:
                break

            tok = self._advance()
            left = self._parse_infix(left, tok)

        return left

    def _can_start_prefix(self, tok: Token) -> bool:
        return tok.type in (TokenType.NUMBER, TokenType.IDENT, TokenType.LPAREN)

    def _get_infix_precedence(self, tok_type: TokenType) -> int:
        if tok_type in (TokenType.PLUS, TokenType.MINUS):
            return self.PREC_ADD
        if tok_type in (TokenType.STAR, TokenType.SLASH):
            return self.PREC_MUL
        if tok_type == TokenType.CARET:
            return self.PREC_POWER
        return self.PREC_LOWEST

    def _parse_prefix(self) -> Node:
        tok = self._advance()

        # Unary +
        if tok.type == TokenType.PLUS:
            return self._parse_expr(self.PREC_PREFIX)

        # Unary -
        if tok.type == TokenType.MINUS:
            operand = self._parse_expr(self.PREC_PREFIX)
            return Negate(operand)

        # Number
        if tok.type == TokenType.NUMBER:
            if '.' in tok.value or 'e' in tok.value or 'E' in tok.value:
                return Constant(float(tok.value))
            return Constant(int(tok.value))

        # Parenthesized expression
        if tok.type == TokenType.LPAREN:
            expr = self._parse_expr(self.PREC_LOWEST)
            self._consume(TokenType.RPAREN, "Missing closing parenthesis ')'")
            return expr

        # Identifier (function, constant, or variable)
        if tok.type == TokenType.IDENT:
            name = tok.value.lower()

            # Check function call: ident followed by '(' or bare argument (e.g. cos 3x, sin x)
            if name in self.FUNCTIONS:
                func_builder = self.FUNCTIONS[name]
                if self._peek().type == TokenType.LPAREN:
                    self._advance()  # consume '('
                    args = []
                    if self._peek().type != TokenType.RPAREN:
                        args.append(self._parse_expr(self.PREC_LOWEST))
                        while self._peek().type == TokenType.COMMA:
                            self._advance()
                            args.append(self._parse_expr(self.PREC_LOWEST))
                    self._consume(TokenType.RPAREN, f"Expected closing ')' for function '{name}'")
                    try:
                        return func_builder(*args)
                    except TypeError as e:
                        raise ParseError(f"Invalid arguments for function '{name}': {e}", self.text, tok.pos)
                elif self._can_start_prefix(self._peek()):
                    # Bare function argument, e.g. cos 3x, sin x, ln x
                    arg = self._parse_expr(self.PREC_MUL)
                    try:
                        return func_builder(arg)
                    except TypeError as e:
                        raise ParseError(f"Invalid bare function call '{name}': {e}", self.text, tok.pos)

            # Check named constant
            if name in self.NAMED_CONSTANTS:
                return self.NAMED_CONSTANTS[name]

            # Variable
            return Variable(tok.value)

        raise ParseError(f"Unexpected token '{tok.value}' in prefix position", self.text, tok.pos)

    def _parse_infix(self, left: Node, op_tok: Token) -> Node:
        if op_tok.type == TokenType.PLUS:
            right = self._parse_expr(self.PREC_ADD)
            return Add(left, right)

        if op_tok.type == TokenType.MINUS:
            right = self._parse_expr(self.PREC_ADD)
            return Subtract(left, right)

        if op_tok.type == TokenType.STAR:
            right = self._parse_expr(self.PREC_MUL)
            return Multiply(left, right)

        if op_tok.type == TokenType.SLASH:
            right = self._parse_expr(self.PREC_MUL)
            return Divide(left, right)

        if op_tok.type == TokenType.CARET:
            # Power is right-associative: pass PREC_POWER - 1
            right = self._parse_expr(self.PREC_POWER - 1)
            return Power(left, right)

        raise ParseError(f"Unexpected operator '{op_tok.value}'", self.text, op_tok.pos)


def parse_expr(expr_str: str) -> Node:
    """High-level function to parse a math string into an AST Node."""
    parser = Parser(expr_str.strip())
    return parser.parse()
