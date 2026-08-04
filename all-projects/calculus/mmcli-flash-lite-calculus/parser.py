"""
Mathematical expression parser supporting tokens, operator precedence,
parentheses, implicit multiplication, and standard mathematical functions.
"""

import math
import re
from typing import List, Union
from .ast_nodes import (
    Node, Number, Variable, Add, Subtract, Multiply, Divide, Power,
    Negate, Sin, Cos, Tan, Log, Exp, Sqrt, Asin, Acos, Atan
)


class TokenType:
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    POWER = "POWER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


class Token:
    def __init__(self, type_: str, value: str, pos: int):
        self.type = type_
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, pos={self.pos})"


class Lexer:
    """Lexical analyzer for mathematical expressions."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self) -> Token:
        pos = self.pos
        result = ""
        decimal_point_seen = False
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if decimal_point_seen:
                    raise ValueError(f"Invalid decimal number at position {self.pos}")
                decimal_point_seen = True
            result += self.current_char
            self.advance()
        
        # Check scientific notation e.g., 1e-3 or 2.5E+4
        if self.current_char is not None and self.current_char in ('e', 'E'):
            result += self.current_char
            self.advance()
            if self.current_char is not None and self.current_char in ('+', '-'):
                result += self.current_char
                self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        return Token(TokenType.NUMBER, result, pos)

    def identifier(self) -> Token:
        pos = self.pos
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token(TokenType.IDENTIFIER, result, pos)

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit() or self.current_char == '.':
                # Check if it's a standalone dot or number
                tokens.append(self.number())
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.identifier())
                continue

            if self.current_char == '+':
                tokens.append(Token(TokenType.PLUS, '+', self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TokenType.MINUS, '-', self.pos))
                self.advance()
            elif self.current_char in ('*', '×', '·'):
                tokens.append(Token(TokenType.MULTIPLY, '*', self.pos))
                self.advance()
            elif self.current_char in ('/', '÷'):
                tokens.append(Token(TokenType.DIVIDE, '/', self.pos))
                self.advance()
            elif self.current_char in ('^', '**'):
                if self.current_char == '*' and self.peek() == '*':
                    self.advance()
                tokens.append(Token(TokenType.POWER, '^', self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.pos))
                self.advance()
            else:
                raise ValueError(f"Unexpected character '{self.current_char}' at position {self.pos}")

        tokens.append(Token(TokenType.EOF, '', self.pos))
        return tokens

    def peek(self) -> Union[str, None]:
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None


class Parser:
    """
    Recursive descent parser for mathematical expressions supporting:
      - Addition, Subtraction, Multiplication, Division, Exponentiation (^ or **)
      - Unary negation (-)
      - Functions: sin, cos, tan, log, ln, exp, sqrt, asin, acos, atan
      - Implicit multiplication (e.g., 2x, 3sin(x), (x+1)(x-1))
    """

    FUNCTION_MAP = {
        'sin': Sin,
        'cos': Cos,
        'tan': Tan,
        'log': Log,
        'ln': Log,
        'exp': Exp,
        'sqrt': Sqrt,
        'asin': Asin,
        'acos': Acos,
        'atan': Atan,
    }

    # Constants recognized automatically
    CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
    }

    def __init__(self, text: str):
        self.text = text
        self.lexer = Lexer(text)
        self.tokens = self.lexer.tokenize()
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def error(self, message: str):
        raise ValueError(f"Parse error at position {self.current_token.pos} ('{self.current_token.value}'): {message}")

    def consume(self, token_type: str):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            self.error(f"Expected token type {token_type}, got {self.current_token.type}")

    def parse(self) -> Node:
        if self.current_token.type == TokenType.EOF:
            return Number(0)
        node = self.expr()
        if self.current_token.type != TokenType.EOF:
            self.error(f"Unexpected trailing token '{self.current_token.value}'")
        return node

    def expr(self) -> Node:
        """expr : term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.consume(TokenType.PLUS)
                node = Add(node, self.term())
            elif token.type == TokenType.MINUS:
                self.consume(TokenType.MINUS)
                node = Subtract(node, self.term())

        return node

    def term(self) -> Node:
        """term : factor (MULTIPLY factor | DIVIDE factor | implicit_factor)*"""
        node = self.factor()

        while True:
            if self.current_token.type == TokenType.MULTIPLY:
                self.consume(TokenType.MULTIPLY)
                node = Multiply(node, self.factor())
            elif self.current_token.type == TokenType.DIVIDE:
                self.consume(TokenType.DIVIDE)
                node = Divide(node, self.factor())
            elif self._is_implicit_multiplication_start():
                # Implicit multiplication e.g. 2 x, x y, 2 (x+1), or sin(x)(x+1)
                node = Multiply(node, self.factor())
            else:
                break

        return node

    def _is_implicit_multiplication_start(self) -> bool:
        """Check if the current token can start implicit multiplication with the previous factor."""
        # Current token can start a factor: NUMBER, IDENTIFIER, LPAREN
        t_type = self.current_token.type
        return t_type in (TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LPAREN)

    def factor(self) -> Node:
        """
        factor : PLUS factor
               | MINUS factor
               | power
        """
        if self.current_token.type == TokenType.PLUS:
            self.consume(TokenType.PLUS)
            return self.factor()
        elif self.current_token.type == TokenType.MINUS:
            self.consume(TokenType.MINUS)
            return Negate(self.factor())
        else:
            return self.power()

    def power(self) -> Node:
        """power : atom (POWER factor)?"""
        node = self.atom()
        if self.current_token.type == TokenType.POWER:
            self.consume(TokenType.POWER)
            # Right associative exponentiation or left associative? Usually right associative: a ^ b ^ c = a ^ (b ^ c)
            exponent = self.factor()
            node = Power(node, exponent)
        return node

    def atom(self) -> Node:
        """
        atom : NUMBER
             | IDENTIFIER (LPAREN expr RPAREN)?
             | LPAREN expr RPAREN
        """
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.consume(TokenType.NUMBER)
            val = token.value
            if '.' in val or 'e' in val.lower():
                return Number(float(val))
            return Number(int(val))

        elif token.type == TokenType.IDENTIFIER:
            name = token.value.lower()
            self.consume(TokenType.IDENTIFIER)

            # Check if constant
            if name in self.CONSTANTS and self.current_token.type != TokenType.LPAREN:
                return Number(self.CONSTANTS[name])

            # Check if function call
            if self.current_token.type == TokenType.LPAREN:
                self.consume(TokenType.LPAREN)
                arg = self.expr()
                self.consume(TokenType.RPAREN)

                if name in self.FUNCTION_MAP:
                    func_cls = self.FUNCTION_MAP[name]
                    return func_cls(arg)
                else:
                    raise ValueError(f"Unknown function '{token.value}'")
            else:
                if name in self.CONSTANTS:
                    return Number(self.CONSTANTS[name])
                return Variable(token.value)

        elif token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            node = self.expr()
            self.consume(TokenType.RPAREN)
            return node

        else:
            self.error(f"Unexpected token '{token.value}'")


def parse_expression(text: str) -> Node:
    """Convenience function to parse a mathematical expression string into an AST."""
    parser = Parser(text)
    return parser.parse()
